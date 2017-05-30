#!/usr/bin/python2
# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

import cv2
import urllib2
import numpy as np
import sys
import threading
import time
import datetime
import Camara

# resized image percentage
size = 100

class Camara_obj(object):
    turn_lock = threading.Lock()
    def __init__(self, cam_name, host):
        self.cam_name = cam_name
        self.host = host
        self.first_image = None

    def run_thread(self):
        with self.turn_lock:
            cam_thread = threading.Thread(target=self.view)
            cam_thread.start()

    def ping_cam():
        # will bring up a back online cam
        # after exception in self.view()
        pass

    def resizeim(self,frame):
        r = float(size) / frame.shape[1]
        dim = (int(size), int(frame.shape[0] * r))
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized

    def show_difference(self,original_image, difference_res):
        thresh = cv2.threshold(difference_res, 20, 255, cv2.THRESH_BINARY)[1]
        # dilate image to "see" more
        thresh = cv2.dilate(thresh, None, iterations=6)

        # mask applied to image
        res = cv2.bitwise_and(original_image , original_image, mask = thresh)
        return res

    def view(self):
        while 1:
            try:
                if len(sys.argv)>1:
                    self.host = sys.argv[1]

                hoststr = 'http://' + self.host + '/video'
                print('Streaming ' + hoststr)

                stream=urllib2.urlopen(hoststr)
                break
            except:
                print("NO DATA FOR: {}".format(self.cam_name))
                return

        bytes=''
        frame_counter = 0
        elapsed_time = 0
        text_overlay = 0
        start_time = time.time()
        while 1:
            try:
                bytes+=stream.read(1024)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a!=-1 and b!=-1:
                    jpg = bytes[a:b+2]
                    bytes= bytes[b+2:]
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(i,'{}'.format(int(text_overlay)),(5,50), font, 1,(255,255,255),2,cv2.LINE_AA)
                    if elapsed_time >= 1.0:
                        # sets frames to overlay variable
                        text_overlay = frame_counter / (time.time() - start_time)
                        frame_counter = 0
                        start_time = time.time()
                        elapsed_time = 0

                    ### keep track of elapsed time
                    end_time = start_time - time.time()
                    elapsed_time -= end_time

                    frame_counter += 1

                    cv2.imshow(self.cam_name, i)

                    #resets initial image
                    self.first_image = None

                    # press "q" to terminate program
                    key = cv2.waitKey(33) & 0xFF

                    if key == ord('q'):
                        exit(0)
            except Exception as e:
                # if not data then break function ending thread
                print('exceptiong happend',e)
                return
                break

def view_all():
    cam1 = Camara_obj('Bedroom',"192.168.1.131:8080")
    cam2 = Camara_obj('House',"192.168.1.144:8080")
    cam3 = Camara_obj('Living Room',"192.168.1.129:8080")

def main():
    cams = Camara.InStore()
    # Prints the list of cams and it's corresponding index number
    for i,key in enumerate(cams.keys()):
        print("{} {}".format(i,key))

    # Get camara number
#    while 1:
#        try:
#            answer = int(raw_input("Choose Camera:\n"))
#            break
#        except Exception as e:
#            print("Not a number\n{}".format(e))
#
    answer = 0
    if answer == 'All':
        cams['All']()
    else:
        for i, key in enumerate(cams.keys()):
            if i == answer:
                answer = key
                print(answer)
                break
        # runs the choses camara
        cam = Camara_obj(answer, cams[answer])
        cam.run_thread()
main()
