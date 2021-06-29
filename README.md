# 프로젝트 구조
- dataset : 이미지 데이터
- models : 모델 가중치 및 config 파일
- static : image, css, js 파일
- templates : rendering될 html 파일
- test_data : 모델 검증에 사용될 테스트 이미지 파일
- ch_dataname.py : data 파일의 이름을 변경하는 script
- cos_similarity.py : 재료탐색에 유사도 검증 후, 만들 수 있는 매뉴 추천 script
- run.py : main flask app 실행

# 가상환경 설치
python -m venv .venv

# 가상환경 실행
source .venv/Scripts/activate

# 가상환경 업그레이드
python -m pip install --upgrade pip

# 프로젝트 필요 모듈 설치
(주의!! 꼭 버전 맞춰서 모듈 설치할 것! 호환성 문제 발생할 수 있음)
pip install -r requirements.txt

# flask 페이지 코드 실행
python run.py

# 06.29. Note
1) 라즈베리파이 OS 환경설정
- pymysql, RPi.GPIO, pandas 라이브러리 설치 필요(pip install pymysql ~)
2) 이미지 인식결과 DATA 저장 구문 예시
- conn = pymysql.connect(host = "localhost", user = "hungry_genie", passwd = "", db = "hungry_genie", charset = "utf8")
- try: with conn.cursor() as cur: sql = "insert into DB values(~)"
- while True: if data is not None: cur.execute(sql, DB SCHEMA) conn.commit(
3) 냉장고 문 열림에 따른 LED 점등 구문 예시
- import RPi.GPIO
- def callback_func(pin): print("냉장고 문 열림 감지, LED 점등") GPIO.output(LED, HIGH)
- GPIO.add_event_detect(pin, GPIO.FALLING, callback=callbakc_func1, bouncetime(200))

# 웹 페이지 구조
1) http://127.0.0.1:5050/ 
=> index 페이지로 yolo frame 결과에 대한 출력

2) http://127.0.0.1:5050/inventory
=> 재고품목에 대해서 알려주는 페이지

3) http://127.0.0.1:5050/recipe
=> 특정 레시피에 대해서 알려주는 페이지

# 주의사항
경로에 한글 포함 시 오류 발생할 수 있음
