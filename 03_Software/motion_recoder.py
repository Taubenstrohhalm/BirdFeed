#!/usr/bin/env python
import imp
import cv2
import numpy as np
import sys
from time import sleep
import requests


# A simple Motion Detection algorithm.
class MotionDetection:
    def __init__(self):
        self.__image0 = np.array([])
        self.__image1 = np.array([])
        self.__image2 = np.array([])
        self._count = 0

        # Configurations
        # Change these to adjust sensitive of motion
        self._MOTION_LEVEL = 2000000
        self._THRESHOLD = 35

    def _updateImage(self, image):
        # print("u")
        self.__image2 = self.__image1
        self.__image1 = self.__image0
        self.__image0 = image

    def _ready(self):
        return self.__image0.size != 0 and self.__image1.size != 0 and self.__image2.size != 0

    def _getMotion(self):
        # print("g")
        if not self._ready():
            return None

        d1 = cv2.absdiff(self.__image1, self.__image0)
        d2 = cv2.absdiff(self.__image2, self.__image0)
        result = cv2.bitwise_and(d1, d2)
        #cv2.imshow('result',result)

        (value, result) = cv2.threshold(result, self._THRESHOLD, 255, cv2.THRESH_BINARY)

        scalar = cv2.sumElems(result)
        #print(f" - scalar:  {scalar[0]} {scalar}")
        return scalar

    def detectMotion(self, image):
        self._updateImage(image)
        # print("d")
        motion = self._getMotion()
        if motion and motion[0] > self._MOTION_LEVEL:
            # print(f"motion scalar: {motion[0]} {motion}")
            return True
        return False


def process():
    # print "Initializing camera..."

    #kicking the esp cam to actualy stream sth
    req = requests.get("http://192.168.178.150", timeout=10)

    #getting the stream
    cap = cv2.VideoCapture("http://192.168.178.150:81/stream")

    
    # print "Initializing the CameraDetection..."
    detection = MotionDetection()

    count = 0

    while True:
        ret, frame = cap.read()

        if frame is None:
            print("no image captured retrying")
            raise Exception("no image")
            sleep(3)
            continue

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        count = count + 1

        if detection.detectMotion(frame):
            print("motion")
            name = f"{count}.jpg"
            ret = cv2.imwrite(name, frame) 
            print(ret)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("main")
    while True:
        try:
            print("try")
            process()

        except KeyboardInterrupt:
            sys.exit()
        
        except Exception as e:
            print(e)
