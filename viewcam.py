##!/usr/bin/python2
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

    def display_motion(self, frame):
        """ should return 3 variables
            1st one should be the frame to dipslay, 
            2nd frameDelta image
            3rd thresh image """
        # crop top text off frame off
        frame_cropped = frame[25::,:] # Crop from x, y, w, h -> 100, 200, 300, 400

        gray = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)


        # sets first frame to compare against another frame for motion
        if self.first_image is None:
            self.first_image = gray
            # 
            return frame, 0, 0 

        # checks both images are of same size
        if self.first_image.shape != gray.shape:
            self.first_image = gray
            # return current frame to stop from comparing 2 diff size images
            return frame, 0, 0



        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(self.first_image, gray)

        # Must set new first_image again for next one to compare against
        self.first_image = gray


        #                                  25 normal
        thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]


        #(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        _,cnts,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        if cnts != []:
            #start_time = time.time()
            for cnt in cnts:
                #print(cv2.contourArea(cnt))
                if cv2.contourArea(cnt) >= 120:
                    # bound rect
                    x, y, w, h = cv2.boundingRect(cnt)
                    # draw contours
                    cv2.rectangle(frame_cropped, (x, y), (x+w, y+h), (0, 255, 0), 2)

        return frame_cropped, frameDelta, thresh
                        
#        thresh = cv2.threshold(self.first_image, 20, 255, cv2.THRESH_BINARY)[1]
#        # dilate image to "see" more
#        thresh = cv2.dilate(thresh, None, iterations=6)
#
#        # mask applied to image
#        res = cv2.bitwise_and(original_image , original_image, mask = thresh)
#
#        #resets initial image
#        #self.first_image = None
#
#        return res
#
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
            # Decoding stream
            bytes+=stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                # image aquisition
                i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                # settings for FPS counter
                font = cv2.FONT_HERSHEY_SIMPLEX
                if elapsed_time >= 1.0:
                    # sets frames to overlay variable
                    text_overlay = frame_counter / (time.time() - start_time)
                    frame_counter = 0
                    start_time = time.time()
                    elapsed_time = 0

                ### keep track of elapsed time for frame counter
                end_time = start_time - time.time()
                elapsed_time -= end_time
                frame_counter += 1

                i, fd, t = self.display_motion(i)

                # sets text over image
                cv2.putText(i,'{}'.format(int(text_overlay)),(5,50), font, 1,(128,128,0),2,cv2.LINE_AA)
                cv2.imshow(self.cam_name, i)
                #cv2.imshow('fd', fd)
                #cv2.imshow('t', t)


                # press "q" to terminate program
                key = cv2.waitKey(33) & 0xFF

                if key == ord('q'):
                    exit(0)

def view_all():
    pass

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
