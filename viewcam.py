#!/usr/bin/python2
# Stream Video with OpenCV from an Android running IP Webcam (https://play.google.com/store/apps/details?id=com.pas.webcam)
# Code Adopted from
# http://stackoverflow.com/questions/21702477/how-to-parse-mjpeg-http-stream-from-ip-camera

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

        # creates a slider for canny values
        cv2.createTrackbar(
            'Low Vals', self.cam_name, 0, 1000, self.do_nothing)
        cv2.createTrackbar(
            'High Vals', self.cam_name, 0, 1000, self.do_nothing)
        # toggle for cany detection

    def run_thread(self):
        with self.turn_lock:
            cam_thread = threading.Thread(target=self.view)
            cam_thread.start()

    def ping_cam():
        # will bring up a back online cam
        # after exception in self.view()
        pass

    def resizeim(self, frame):
        r = float(size) / frame.shape[1]
        dim = (int(size), int(frame.shape[0] * r))
        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        return resized

    def show_difference(self, original_image, difference_res):
        thresh = cv2.threshold(difference_res, 20, 255, cv2.THRESH_BINARY)[1]
        # dilate image to "see" more
        thresh = cv2.dilate(thresh, None, iterations=6)

        # mask applied to image
        res = cv2.bitwise_and(original_image, original_image, mask=thresh)
        return res

    def canny_edged(self, original_image, canny_low_val, canny_high_val):
        cannied = cv2.Canny(original_image, canny_low_val, canny_high_val)

        return cannied

    def do_nothing(self, *args, **kwargs):
        pass

    def view(self):
        while 1:
            try:
                if len(sys.argv) > 1:
                    self.host = sys.argv[1]

                hoststr = 'http://' + self.host + '/video'
                print('Streaming ' + hoststr)

                stream = urllib2.urlopen(hoststr)
                break
            except:
                print("NO DATA FOR: {}".format(self.cam_name))
                return

        bytes = ''
        frame_counter = 0
        elapsed_time = 0
        text_overlay = 0
        start_time = time.time()
        while 1:
            try:
                bytes += stream.read(1024)
                a = bytes.find('\xff\xd8')
                b = bytes.find('\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes[a:b + 2]
                    bytes = bytes[b + 2:]
                    # cv2 version 2
                    # i = cv2.imdecode(
                    # np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
                    # cv2 version 3
                    i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(i, '{}'.format(int(text_overlay)), (5, 50),
                                font, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    # crop top of image
#                    i = i[25::,:] # crop from x, y , w, h

                    #>>>compute movements
#                    def find_movement(self, original_image):
#                        gray = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
#
#                        # Sets initial image to cmopare to
#                        if self.first_image is None:
#                            self.first_image = gray
#                            return 0
#
#                    # Finds the difference bwetween 2 images
#                    frameDelta = cv2.absdiff(self.first_image, gray)
#                    # diff of images to original image
#                    res = self.show_difference(i,frameDelta)
                    #<<<

                    #>>> compute coords of blocks of movement
#                    _, contours, _ = cv2.findContours(
                    # frameDelta.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#                    for cnt in contours:
#                        #print("size:{} Area:{}".format(cnt.size,cv2.contourArea(cnt)))
#                        # if contour size is less than 10 set to 0 on frameDelta
#                        # get coords of cnt
#                        # find coords of contour
#                    pixelpoints = cv2.findNonZero(frameDelta)
#                    print(pixelpoints)
                    #<<<

                    # Show images
                    # shows spots of movements
                    # cv2.imshow(self.cam_name,res)
                    # shows difference in binary
                    # cv2.imshow(self.cam_name+'thresh', frameDelta)
                    # tracks 1 second
                    if elapsed_time >= 1.0:
                        # sets frames to overlay variable
                        # text_overlay = frame_counter
                        text_overlay = frame_counter / (time.time() - start_time)
                        frame_counter = 0
                        start_time = time.time()
                        elapsed_time = 0

                    # keep track of elapsed time
                    end_time = start_time - time.time()
                    elapsed_time -= end_time

                    frame_counter += 1

                    low_val = cv2.getTrackbarPos('Low Vals', self.cam_name)
                    high_val = cv2.getTrackbarPos('High Vals', self.cam_name)

                    cv2.createTrackbar(
                        'Low Vals', self.cam_name, low_val, 1000, self.do_nothing)
                    cv2.createTrackbar(
                        'High Vals', self.cam_name, high_val, 1000, self.do_nothing)

                    # passes values to func
                    if low_val != 0 or high_val != 0:
                        i = self.canny_edged(i, low_val, high_val)

                    # Displays frames
                    cv2.imshow(self.cam_name, i)

                    # resets initial image
                    self.first_image = None

                    # press "q" to terminate program
                    key = cv2.waitKey(33) & 0xFF

                    if key == ord('q'):
                        exit(0)
            except Exception as e:
                # if not data then break function ending thread
                print('exceptiong happend', e)
                return
                break


def view_all():
    cam1 = Camara_obj('Bedroom', "192.168.1.131:8080")
    cam2 = Camara_obj('House', "192.168.1.144:8080")
    cam3 = Camara_obj('Living Room', "192.168.1.129:8080")


def main():
    cams = Camara.InStore()
    # Prints the list of cams and it's corresponding index number
    for i, key in enumerate(cams.keys()):
        print("{} {}".format(i, key))

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


# dictionary of all the camaras
# cams = {
#'Bedroom':Camara_obj('Bedroom',"192.168.1.144:8080"),
#'House':Camara_obj('House',"192.168.0.107:8080"),
#'Living Room':Camara_obj('Living Room',"192.168.1.131:8080"),
#'lg':Camara_obj('LG','192.168.1.122:8080'),
#}

main()