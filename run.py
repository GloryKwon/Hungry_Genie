import os
import cv2
import numpy as np
import pymysql
from flask import Flask, render_template, request, make_response,Response
from cos_similarity import menu_recommend
from settings.config import DB_INFO

# DB 접속
conn = pymysql.connect(
       host=DB_INFO['host'],
       port=DB_INFO['port'],
       user=DB_INFO['user'],
       password=DB_INFO['password'],
       db=DB_INFO['db'],
       charset=DB_INFO['charset'])

curs = conn.cursor()

# 경로 설정
DIR_PATH = os.path.dirname(os.path.realpath(__file__))

# DB mapping dict
ingredient = {
    'apple':'사과', 'bacon':'베이컨', 'carrot':'당근', 'cheese':'치즈', 'chicken':'닭고기', 'egg':'계란',
    'kimchi':'배추김치', 'milk':'우유', 'onion':'양파', 'paprika':'파프리카','potato':'감자', 'rotten_apple':'상한사과', 'shrimp':'새우'
}

# Flask App 생성
app = Flask(__name__)

# yolo 결과를 토대로 db data update
def update_db(data_dict) :
    for ingred in data_dict.keys() :   
        ch_ingredient = ingredient[ingred]
        ch_num = data_dict[ingred]
        sql = f"update frige set num = '{ch_num}' where ingredient = '{ch_ingredient}'"
        curs.execute(sql)
        conn.commit()

# image yolo 모델 통과
def yolo(frame, size, score_threshold, nms_threshold, dir_path):

    # 경로 설정
    yolo_custom_weights = dir_path + "\models\yolov4-custom.weights"
    yolo_custom_cfg = dir_path + "\models\yolov4-custom.cfg"

    # yolo 관련 설정
    classes = ["apple", "bacon", "carrot", "cheese", "chicken", "egg", "kimchi", "milk", "onion", "paprika", "potato", "rotten_apple", "shrimp"]
    net = cv2.dnn.readNet(yolo_custom_weights, yolo_custom_cfg)
    colors = np.random.uniform(0, 255, size=(len(classes),3))
    
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # 이미지의 높이, 너비, 채널 받아오기
    height, width, channels = frame.shape

    # 네트워크에 넣기 위한 전처리
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (size, size), (0, 0, 0), True, crop=False)

    # 전처리된 blob 네트워크에 입력
    net.setInput(blob)

    # 결과 받아오기
    outs = net.forward(output_layers)

    # 각각의 데이터를 저장할 리스트 생성 및 초기화
    class_ids = []
    confidences = []
    boxes = []
    class_dict = {}

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # 정확도가 0.75보다 크다면 bounding box를 칠한다.
            if confidence > 0.45:
                # 탐지된 객체의 너비, 높이 및 중앙 좌표값 찾기
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 객체의 사각형 테두리 중 좌상단 좌표값 찾기
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 노이즈 제거 (Non Maximum Suppression) (겹쳐있는 박스 중 상자가 물체일 확률이 가장 높은 박스만 남겨둠)
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=score_threshold, nms_threshold=nms_threshold)

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            class_name = classes[class_ids[i]]

            # 프레임에 작성할 텍스트 및 색깔 지정
            label = f"{class_name}: {confidences[i]:.2f}"

            color = colors[class_ids[i]]

            # 프레임에 사각형 테두리 그리기 및 텍스트 쓰기
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(frame, (x - 1, y), (x + len(class_name) * 13 + 80, y - 25), color, -1)
            cv2.putText(frame, label, (x, y - 8), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2)
            
            if class_name == 'rotten_apple' :
                continue

            if class_name not in class_dict.keys() :
                class_dict[class_name] = 1
            else :
                class_dict[class_name] += 1

    update_db(class_dict)
    return frame

def gen_frames() :
    
    frame = cv2.imread(DIR_PATH + "/test_data/test.jpg")
    
    if frame is None :
        print("이미지가 없습니다.")
    
    else :
        frame = yolo(frame=frame, size=416, score_threshold=0.45, nms_threshold=0.4, dir_path=DIR_PATH)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # concat frame one by one and show result
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  
        cv2.destroyAllWindows()

# Flask page routing
@app.route('/')
def home() :
    return render_template('index.html') 

@app.route('/capture')
def capture() :
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/inventory')
def inventory() :
    return render_template('inventory.html')

@app.route('/recipe')
def recipe() :
    value = menu_recommend(DIR_PATH, curs)
    return render_template('recipe.html', value = value)

if __name__ == '__main__' :
    app.run(host='127.0.0.1', port=5050, debug=True)
