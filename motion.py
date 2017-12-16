#!/usr/bin/python2
import cv2 
import urllib2
import numpy as np
import sys
import datetime
import time 
import os
import threading
import Camara
#import multiprocessing
run = True

class Cam(object):
    global run
    def __init__(self, cam_name, host):
        self.cam_name = cam_name 
        self.host = host
        self.online_switch = True
        self.firstFrame = None
        self.turn = threading.Lock()
        #self.save_folder = 'sec-imgs'
        self.save_folder = Camara.save_folder()
        #self.save_folder = '/run/user/1000/gvfs/smb-share:server=192.168.ec-imgs' 

        #object_process = multiprocessing.Process(target=self.run_motion_detection)
        object_process = threading.Thread(target=self.run_motion_detection)
        object_process.start()
        
    def cvt2Contour(self,i):
        imgray = cv2.cvtColor(i, cv2.COLOR_BGR2GRAY)

        ih,iw,_ = i.shape
        # new image of same size but black
        i = np.zeros((ih,iw,3),np.uint8)

        counts = 100
        for _ in xrange(6):
            ret, thresh = cv2.threshold(imgray, counts,255,0)
            _,contours , hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cv2.drawContours(i, contours, -1, (255,255,255),1)
            counts += 25
        return i

    def viewMotions(self, frame):
        pass

    def cam_connectivity(self):
        global run
        # Checks cam's connection every 5 mins
        # returns if ONLINE
        while run:
            try:
                urllib2.urlopen('http://' + self.host + '/video')
            except Exception as e:
                print(e)
                if self.online_switch:
                    print("\n{} {}...OFFLINE\n".format(datetime.datetime.now().strftime("%F %H:%M"), self.cam_name))
                    self.online_switch = False
                for _ in xrange(60):
                    if not run:
                        break
                    time.sleep(1)
            else:
                self.online_switch =  True
                return "online"

    def run_motion_detection(self):
        stream = None
        # giant loop to keep connections alive w/o killing thread
        while run:
            if len(sys.argv)>1:
                self.host = sys.argv[1]

            hoststr = 'http://' + self.host + '/video'
            #print('Streaming {}\n'.format(hoststr))

            # Checks if cam is online
            while run:
                # continues to next block only after cam online
                try:
                    stream=urllib2.urlopen(hoststr)
                    print("\n{}...{}[{}] ONLINE".format(datetime.datetime.now().strftime("%F %H:%M"),self.cam_name,self.host))
                    break
                except Exception as e:
                    print(e)
                    if self.cam_connectivity() == 'online':
                        break

            bytes=''

            while run:
                try:
                    bytes+=stream.read(1024)
                    a = bytes.find('\xff\xd8')
                    b = bytes.find('\xff\xd9')
                    if a == -1 and b == -1:
                        # no connection if both -1
                        # break to check connection
                        break
                    if a!=-1 and b!=-1:
                        jpg = bytes[a:b+2]
                        bytes= bytes[b+2:]
                        # cv2 version 2
                        #frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
                        # cv2 version 3
                        frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)

                        # crop top text off frame off
                        frame_cropped = frame[25::,:] # Crop from x, y, w, h -> 100, 200, 300, 400

                        gray = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2GRAY)
                        #gray = cv2.GaussianBlur(gray, (21, 21), 0)

                        if self.firstFrame is None:
                            self.firstFrame = gray
                            continue

                        
                        # compute the absolute difference between the current frame and first frame
                        frameDelta = cv2.absdiff(self.firstFrame, gray)
                        #                                  25 normal
                        thresh = cv2.threshold(frameDelta, 50, 255, cv2.THRESH_BINARY)[1]
			# works in rpi3 debian 
                        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                        #_,cnts,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

                        if cnts != []:
                            try:
                                #start_time = time.time()
                                for cnt in cnts:
                                    if cv2.contourArea(cnt) >= 120:
                                        cv2.imwrite(self.save_folder+'/{}.png'.format(datetime.datetime.now().strftime("%H:%M:%S:%f-%F")), frame)
                                        break

                            except Exception as e:
                                print(e)
                                print("saved FAIL")

                            #time.sleep(1)
                            ### Motion anabled detection
                            self.firstFrame = None
                            continue
                        ### continuous rec
#                        self.firstFrame = None

                except Exception as e:
                    # another check
                    print('second exception broken',e)
                    break
                
                def compute_motion(first_frame, sec_frame):
                    pass

def stop_threads():
    global run
    # run stops all while loops, ending threads
    x = raw_input("Press ENTER to stop\n\n")
    run = False
    print("STOPING ALL THREADS!")

# asks to press enter to stop threads
stop_thread = threading.Thread(target=stop_threads)
stop_thread.start()

cams_dict = Camara.InStore()

# creates and runs recording on each object
for key in cams_dict:
    Cam(key, cams_dict[key])
