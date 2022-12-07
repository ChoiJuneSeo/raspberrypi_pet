import pygame
from cvlib.object_detection import YOLO
import cv2
from time import localtime
import pyrebase
import json

with open('/home/asus/project/auth.json') as f :
    config = json.load(f)
firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

pygame.mixer.init()
full = pygame.mixer.Sound('/home/asus/Music/full.wav')
empty = pygame.mixer.Sound('/home/asus/Music/empty.wav')

picam = cv2.VideoCapture(0)
weights = "full_empty.weights"
config = "yolov4-tiny-custom.cfg"
labels = "obj.names"
model = YOLO(weights, config, labels)
cnt = 0
#시작하기 전 변수 초기화
Full_count = 0
Empty_count = 0
Status = 'none'

def Update_Time(): # 현재시간을 문자열로 저장하여 반환하는 함수
    print("Update time")
    tm = localtime()
    st_y = str(tm.tm_year)
    st_m = str(tm.tm_mon)
    st_d = str(tm.tm_mday)
    st_h = str(tm.tm_hour)
    st_min = str(tm.tm_min)
    st_s = str(tm.tm_sec)
    Uptime = st_y+"_"+st_m+"_"+st_d+"_"+st_h+"_"+st_min+"_"+st_s
    return Uptime

def Upload_data(a,b): # 데이터베이스에 데이터를 저장하는 함수
    Data = {a:b}
    db.child("Pet").update(Data)
    cv2.imwrite("/home/asus/Pictures/{}.jpg" .format(a) , img)
    storage.child("Pet/image/{0}/{1}.jpg" .format(b,a)).put("/home/asus/Pictures/{}.jpg" .format(a))
    
def Load_data(Key): # 데이터베이스에 저장되어 있는 페트병 상태룰 불러오는 함수
    print("Load data")
    Value = db.child("Pet").get().val().get(Key)
    return Value
   
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
    
    print("Full_count : {}" .format(Full_count))
    print("Empty_count : {}" .format(Empty_count))
    print("Status = {}" .format(Status))
    if cnt % 10 == 0:
        if label == ['full']:
            Full_count += 1
        if label == ['empty']:
            Empty_count += 1
    if Full_count > 0 and Empty_count > 0:
        Full_count = 0
        Empty_count = 0 
        
    if Full_count == 4:
        status = 'Full'
        Time = Update_Time()
        Upload_data(Time,status)
        Status = Load_data(Time)
        Full_count = 0

    if Empty_count == 4:
        status = 'Empty'
        Time = Update_Time()
        Upload_data(Time,status)
        Status = Load_data(Time)
        Empty_count = 0
    
    if Status == 'Full':
        full.play()
        Status = 'None'
    if Status == 'Empty':
        empty.play()
        Status = 'None'

    if  cv2.waitKey(1) & 0xFF == ord('q'):
        break
