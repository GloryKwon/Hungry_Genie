from numpy import dot
from numpy.linalg import norm
import numpy as np
import pandas as pd
import re
import pymysql

def cos_similarity(A, B):
       return dot(A, B)/(norm(A)*norm(B))  # cosine similarity

def menu_recommend(DIR_PATH, curs): #절대 경로, db 커서
    #레시피 데이터
    data = pd.read_csv(DIR_PATH+'/static/assets/recipe.csv', encoding = 'cp949')  # 데이터 호출
    menu = list(data['메뉴'].dropna())
    need = list(data['필수재료'].dropna())
    sub = list(data['부가재료'].fillna(' '))
    recipe = list(data['레시피'].fillna(' '))
    img = list(data['이미지'].fillna(' '))
    #현재 냉장고 재고 쿼리
    sql_i = "select ingredient from frige"
    sql_n = "select num from frige"
    curs.execute(sql_i)
    ingredient = pd.DataFrame(curs.fetchall())[0].tolist()
    curs.execute(sql_n)
    num_ingre = pd.DataFrame(curs.fetchall())[0].tolist()

    impossible = {}
    cos_sim = []
    food = {}

    for i, m in enumerate(menu):
        food[m] = need[i]    # 음식과 재료 데이터

    for k, v in food.items():
        having = list(num_ingre) # 현재 재료 보유 현황
        necessary = [0 for _ in range(len(num_ingre))] # 필요 재료 현황
        v = re.split(', | ', v)
        for i in range(len(v)//2):
            if v[i*2] in ingredient:  # 재료가 있다면 
                necessary[ingredient.index(v[i*2])] = int(v[i*2+1])  # 필수 재료 데이터 입력
                if having[ingredient.index(v[i*2])] < necessary[ingredient.index(v[i*2])]: # 재료가 부족한 상황
                    if k in impossible:
                        impossible[k] += " "+v[i*2]+" "+str(necessary[ingredient.index(v[i*2])]-having[ingredient.index(v[i*2])])
                    else:
                        impossible[k] = v[i*2]+" "+str(necessary[ingredient.index(v[i*2])]-having[ingredient.index(v[i*2])]) # 불가능 개수
            else:  # 재료가 없다면
                if k in impossible:
                    impossible[k] += " "+v[i*2]+" "+v[i*2+1]
                else:
                    impossible[k] = v[i*2]+" "+v[i*2+1]
                
        if sub[menu.index(k)] != ' ':
            v = sub[menu.index(k)]
            v = re.split(', | ', v)
            for i in range(len(v)//2):
                if v[i*2] in ingredient:  # 재료가 있다면 
                    necessary[ingredient.index(v[i*2])] = int(v[i*2+1])
                else:
                    necessary.append(int(v[i*2+1]))
                    
        while len(having) < len(necessary):
            having.append(0)   # vector 크기 맞춤
        
        if k in impossible:
            cos_sim.append([round(cos_similarity(having, necessary), 5), k, menu.index(k)])
            #만들 수 없는 경우만 존재한다면 그 중에서도 높은 값을 출력해주기 위해 수정
        else:
            for i in range(len(having)):
                if having[i] > necessary[i]: # 재료가 더 많아도 cos_sim 크기 지장 없게
                    having[i] = necessary[i]
            cos_sim.append([round(cos_similarity(having, necessary), 5), k, menu.index(k)])

    cos_sim = sorted(cos_sim, key = lambda x : x[0], reverse = True)
    idx = cos_sim[0][2]
    rec_name = cos_sim[0][1]
    if rec_name in impossible: #재료가 모두 준비된 레시피가 없는 경우
        value = [rec_name, recipe[idx], img[idx], impossible[rec_name]] #레시피명, 레시피 내용, 이미지
    else: #재료가 모두 준비된 레시피가 있는 경우
        value = [rec_name, recipe[idx], img[idx], 0] #레시피명, 레시피 내용, 이미지
    return value

