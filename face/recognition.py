import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np 
import pickle
import RPi.GPIO as GPIO
from time import sleep
import I2C_LCD_driver
mylcd=I2C_LCD_driver.lcd()
relay_pin = [23]
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_pin, GPIO.OUT)
GPIO.output(relay_pin, 0)

with open('labels', 'rb') as f:
    dict = pickle.load(f)
    label = {v:k for k,v in dict.items() }
    f.close()

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(640, 480))


faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainer.yml")

font = cv2.FONT_HERSHEY_SIMPLEX

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = frame.array
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 4)
    for (x, y, w, h) in faces:
        roiGray = gray[y:y+h, x:x+w]

        id_, conf = recognizer.predict(roiGray)

        for name, value in dict.items():
            if value == id_:
                print(name)

        if conf < 45:
            name = label[id_]
        
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, name, (x, y), font, 2, (0, 0 ,255), 2,cv2.LINE_AA)
            #sleep(4)
            GPIO.output(relay_pin, 1)
            
            mylcd.lcd_display_string("DOOR UNLOCK!!",1)
            

        else:
            GPIO.output(relay_pin, 0)
            mylcd.lcd_display_string("Stranger!!",1)
            print("stranger")
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
            

    cv2.imshow('frame', frame)
    key = cv2.waitKey(1)

    rawCapture.truncate(0)
    if key == 20:
        GPIO.output(relay_pin, 0)

    if key == 27:
        break

cv2.destroyAllWindows()