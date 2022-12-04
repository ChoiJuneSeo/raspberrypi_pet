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
    if cnt % 50 == 0 and label == ['full']:
        tm = localtime()
        st_y = str(tm.tm_year)
        st_m = str(tm.tm_mon)
        st_d = str(tm.tm_mday)
        st_h = str(tm.tm_hour)
        st_min = str(tm.tm_min)
        st_s = str(tm.tm_sec)
        Time = st_y+"_"+st_m+"_"+st_d+"_"+st_h+":"+st_min+":"+st_s
        value = 1
        Data = {Time : value}
        db.child("Pet").update(Data)
        cv2.imwrite("/home/asus/Pictures/{}.jpg" .format(Time) , img)
        storage.child("Pet/image/full/{}.jpg" .format(Time)).put("/home/asus/Pictures/{}.jpg" .format(Time))
        full.play()
        
    if cnt % 30 == 0 and label == ['empty']:
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
        empty.play()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
