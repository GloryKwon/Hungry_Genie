from numpy import dot
from numpy.linalg import norm
import numpy as np
import pandas as pd
import re

def cos_similarity(A, B):
       return dot(A, B)/(norm(A)*norm(B))  # cosine similarity

data = pd.read_csv('C:/Users/user/Desktop/메뉴 및 재료.csv', encoding = 'cp949')  # 데이터 호출

ingredient = list(data['재료'])
num_ingre = list(data['개수'])
menu = list(data['메뉴'].dropna())
need = list(data['필수재료'].dropna())
sub = list(data['부가재료'].fillna(' '))
impossible = {}
cos_sim = {}

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
                    impossible[k] += v[i*2]+str(necessary[ingredient.index(v[i*2])]-having[ingredient.index(v[i*2])])
                else:
                    impossible[k] = v[i*2]+str(necessary[ingredient.index(v[i*2])]-having[ingredient.index(v[i*2])]) # 불가능 개수
        else:  # 재료가 없다면
            if k in impossible:
                impossible[k] += v[i*2]+v[i*2+1]
            else:
                impossible[k] = v[i*2]+v[i*2+1]
            
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
        cos_sim[k] = 0  # 만들 수 없으면 cos_sim = 0
    else:
        for i in range(len(having)):
            if having[i] > necessary[i]: # 재료가 더 많아도 cos_sim 크기 지장 없게
                having[i] = necessary[i]
        cos_sim[k] = round(cos_similarity(having, necessary), 5)

cos_sim = sorted(cos_sim.items(), key = lambda x : x[1], reverse = True)
print(cos_sim)
print(impossible)

