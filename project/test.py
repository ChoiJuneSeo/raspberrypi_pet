import pyrebase
import json
import time
from time import localtime
import pygame
from cvlib.object_detection import YOLO
import cv2


tm = localtime()

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
        full.play()
    if cnt % 30 == 0 and label == ['empty']:
        tm = localtime()
        st_y = str(tm.tm_year)
        st_m = str(tm.tm_mon)
        st_d = str(tm.tm_mday)
        st_h = str(tm.tm_hour)
        st_min = str(tm.tm_min)
        st_s = str(tm.tm_sec)
        Time = st_y+"_"+st_m+"_"+st_d+"_"+st_h+":"+st_min+":"+st_s
        cv2.imwrite("/home/asus/Pictures/{}.jpg" .format(Time) , img)
        empty.play()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
