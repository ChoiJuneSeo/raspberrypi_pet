import pygame
from cvlib.object_detection import YOLO
import cv2

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
    if cnt % 50 == 0 and label == ['empty']:
        empty.play()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
