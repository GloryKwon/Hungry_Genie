# dataset 폴더안에 있는 이미지 폴더(및 파일)의 이름을 수정하는 python script입니다.

import os

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
data_path = DIR_PATH + '/dataset'
folder_names = os.listdir(data_path)

for folder in folder_names :
    file_path = data_path + '/' + folder
    file_names = os.listdir(file_path)

    i = 1
    for file in file_names :
        src = os.path.join(file_path, file)
        dst = folder + '_' + str(i) + '.jpg'
        dst = os.path.join(file_path, dst)
        os.rename(src, dst)
        i = i + 1

    print('Done!', folder)