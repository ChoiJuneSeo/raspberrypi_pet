#print문들은 대체로 오류가 났을 시 어디서 났는지 확인하기 위한 용도로 넣어놨습니다.
import pygame
from cvlib.object_detection import YOLO
import cv2
import pyrebase
import json
import time
from time import localtime
with open('/home/asus/project/auth.json') as f :
    config = json.load(f)
firebase = pyrebase.initialize_app(config)

db = firebase.database()
storage = firebase.storage()
value = 0

pygame.mixer.init()
full = pygame.mixer.Sound('/home/asus/Music/full.wav')
empty = pygame.mixer.Sound('/home/asus/Music/empty.wav')

picam = cv2.VideoCapture(0)
weights = "full_empty.weights"
config = "yolov4-tiny-custom.cfg"
labels = "obj.names"
model = YOLO(weights, config, labels)
cnt = 0
Full_count = 0
Empty_count = 0
process = 0     #코드 진행 단계 (변수 값을 조건으로 if문을 실행시킬 건데 그렇게 하면 변수값이 바뀌기 전까지 계속 실행되서 오류가 날 수도 있지 않을까...?해서 코드 진행단계를 추가했습니다.
#코드가 문제없이 잘 작동하길래 없어도 되는지는 확인하지 않았습니다...)

if not picam.isOpened():
    print('picam is not working')
    exit()

while picam.isOpened:
    ret, img = picam.read()
    cnt += 1
    if cnt % 10 != 0:
        continue
    image = cv2.resize(img, (680,460))
    bbox, label, conf = model.detect_objects(image)
    detect_image = model.draw_bbox(image, bbox, label, conf)
    print('count : {} || detect : {}'.format(int(cnt/10), label))
    cv2.imshow("detect", image)
    #1초마다 체크해서 label이 full이면 Full_count 1스택
    if cnt % 10 == 0 and label == ['full']:
        Full_count += 1
        print(Full_count)
    #1초마다 체크해서 label이 empty면 empty_count 1스택
    if cnt % 10 == 0 and label == ['empty']:
        Empty_count += 1
        print(Empty_count)
    if Full_count == 3 and process == 0:#Full_count 3스택 쌓이고 현재 진행단계가 0일 경우
        tm = localtime()#현재 시간 불러오기
        st_y = str(tm.tm_year)
        st_m = str(tm.tm_mon)
        st_d = str(tm.tm_mday)
        st_h = str(tm.tm_hour)
        st_min = str(tm.tm_min)
        st_s = str(tm.tm_sec)
        Time = st_y+"_"+st_m+"_"+st_d+"_"+st_h+":"+st_min+":"+st_s
        value = 1
        Data = {Time : value}#데이터베이스에 갱신시킬 딕셔너리
        db.child("Pet").update(Data)#데이터베이스에 올리기
        cv2.imwrite("/home/asus/Pictures/{}.jpg" .format(Time) , img)#라즈베리파이 폴더에 사진 저장
        storage.child("Pet/image/full/{}.jpg" .format(Time)).put("/home/asus/Pictures/{}.jpg" .format(Time))#저장한 사진을 데이터베이스에 올리기
        Full_count = 0 #둘 중 한개는 3스택 쌓였으니까 초기화 
        Empty_count = 0 #둘 중 한개는 3스택 쌓였으니까 초기화
        process += 1 #진행 단계를 1단계로 바꿈
        print(Full_count)
        print(Empty_count)
    if Empty_count == 3 and process == 0:# Empty_count 3스택 + 0단계일 때 실행
        tm = localtime()
        st_y = str(tm.tm_year)
        st_m = str(tm.tm_mon)
        st_d = str(tm.tm_mday)
        st_h = str(tm.tm_hour)
        st_min = str(tm.tm_min)
        st_s = str(tm.tm_sec)
        Time = st_y+"_"+st_m+"_"+st_d+"_"+st_h+"_"+st_min+"_"+st_s
        value = 0
        Data = {Time : value}
        db.child("Pet").update(Data)
        cv2.imwrite("/home/asus/Pictures/{}.jpg" .format(Time) , img)
        storage.child("Pet/image/empty/{}.jpg" .format(Time)).put("/home/asus/Pictures/{}.jpg" .format(Time))
        Full_count = 0
        Empty_count = 0
        process += 1
        print(Full_count)
        print(Empty_count)
    if  process == 1:#진행단계가 1단계일 때 실행 = 무엇인가 3스택이 쌓였을 때
        A = db.child("Pet").get()#데이터베이스의 Pet의 값을 불러옴 (.val()과 같이 써야함)
        B = A.val()#불러온 값을 딕셔너리 형태로 가져오는데, OrderedDict(Time : value) 이런 느낌으로 불러와서 써먹기 불편했습니다.
        Status = B.get(Time)#그래서 Time의 값인 value만 불러주면 0 또는 1을 얻을 수 있습니다.
        process += 1 #다음 단계로 (2단계)
    if  process == 2:#2단계
        if Status == 1:#Status는 데이터베이스의 Time의 키값, 즉 0 또는 1입니다.
            full.play()
            process = 0# 다 끝냈으니 다시 0단계로 돌아가 다음을 준비합니다.
        if Status == 0:
            empty.play()
            process = 0
    if  cv2.waitKey(1) & 0xFF == ord('q'):
        break
