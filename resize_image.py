import os
import cv2

# 경로 설정
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
data_path = DIR_PATH + '/dataset'
folder_names = os.listdir(data_path)

for folder in folder_names :
    if folder != 'mydata' :
        continue
    
    file_path = data_path + '/' + folder
    file_names = os.listdir(file_path)

    for file in file_names : 
        src = os.path.join(file_path, file)
        dst_path = data_path + '/' + 'resize_data'
        dst = os.path.join(dst_path,file)

        img = cv2.imread(src)
        img = cv2.resize(img, (416,416), interpolation = cv2.INTER_AREA)

        cv2.imshow('Scaling Size', img)
        cv2.waitKey(0)

        cv2.imwrite(dst,img)