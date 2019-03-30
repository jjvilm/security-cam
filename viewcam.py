#!/usr/bin/python3
import cv2
import numpy as np
import threading
import time
import datetime
import CamSettings 

# resized image percentage
size = 100

class Camara_obj(object):
    turn_lock = threading.Lock()
    def __init__(self, cam_name, host):
        self.cam_name = cam_name
        self.host = host
        self.first_image = None
        # use to toggle shown frames on screen
        self.imageFilterToggle = 0
        self.showDelta = 0
        self.showThresh = 0
        self.showThreshErosion = 0
        self.frame_top = 0
        self.frame_btm = 0
        self.frame_rgt = 0
        self.frame_lft = 0
        # settings 
        self.contourAreaValue = 90
        self.thresholdValue = 50
        self.kernelValue = 1
        self.quality_toggle = False

    def run_thread(self):
        with self.turn_lock:
            cam_thread = threading.Thread(target=self.view)
            cam_thread.start()

    def resizeim(self,frame):
        r = float(size) / frame.shape[1]
        dim = (int(size), int(frame.shape[0] * r))
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized

    def display_motion(self, frame):
        """ should return 4 variables
            1st one should be the frame to dipslay, 
            2nd frameDelta image
            3rd thresh image, 4th threshErosion """
        # crop top text off frame off
        # to avoid motion detection from time stamp
        frame_cropped = frame[25::,:] # Crop from x, y, w, h -> 100, 200, 300, 400

        gray = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2GRAY)
        #gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # sets first frame to compare against another frame for motion
        if self.first_image is None:
            self.first_image = gray
            return frame, 0, 0, 0

        # checks both images are of same size
        if self.first_image.shape != gray.shape:
            self.first_image = gray
            # return current frame to stop from comparing 2 diff size images
            return frame, 0, 0, 0

        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(self.first_image, gray)

        # Must set new first_image again for next one to compare against
        self.first_image = gray
        #                                  25 normal
        thresh = cv2.threshold(frameDelta, self.thresholdValue, 255, cv2.THRESH_BINARY)[1]
        # works with python3, cv2, archlinux ver
        cnts,_ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        if cnts != []:
            #start_time = time.time()
            for cnt in cnts:
                #print(cv2.contourArea(cnt))
                if cv2.contourArea(cnt) >= self.contourAreaValue:
                    #print(cv2.contourArea(cnt))
                    # bound rect
                    x, y, w, h = cv2.boundingRect(cnt)
                    # draw contours
                    cv2.rectangle(frame_cropped, (x, y), (x+w, y+h), (0, 255, 0), 1)

        return frame_cropped, frameDelta, thresh, 0#threshErosion
                        
    def findBrightness(self, frame):
        try:
            if frame == None:
                return
        except:
            pass

        # Convert to gray
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        values = []
        for x in frame:
            avg = sum(x) / len(x)
            values.append(avg)
        avg = sum(values) / len(values)
        return avg

    def view(self):
        hoststr = 'http://' + self.host + '/video'
        stream = cv2.VideoCapture(hoststr)
        frame_counter = 0
        elapsed_time = 0
        text_overlay = 0
        start_time = time.time()

        while 1:
            ret, frame = stream.read()

            # font settings for FPS counter
            font = cv2.FONT_HERSHEY_SIMPLEX

            ### keep track of elapsed time for frame counter
            if elapsed_time >= 1.0:
                # sets frames to overlay variable
                text_overlay = frame_counter / (time.time() - start_time)
                frame_counter = 0
                start_time = time.time()
                elapsed_time = 0

            end_time = start_time - time.time()
            elapsed_time -= end_time
            frame_counter += 1

            if self.imageFilterToggle:
                # returns applied filters
                # original image, frameDelta, Threshold images
                frame, fd, t, threshErosion = self.display_motion(frame)

            # sets text over image
            cv2.putText(frame,'{}'.format(int(text_overlay)),(5,50), font, 1,(0,255,0),2,cv2.LINE_AA)
            # Displays original frame
            cv2.imshow(self.cam_name, frame)

            # toggleble filters display
            if self.imageFilterToggle:
                if self.showDelta:
                    cv2.imshow('Delta', fd)
                if self.showThresh:
                    cv2.imshow('Thresh', t)
                if self.showThreshErosion:
                    cv2.imshow('Thresh Erosion', threshErosion)


            # press "q" to terminate program
            key = cv2.waitKey(33) & 0xFF
            if key == ord('q'):
                exit(0)

            # toggles thresh image displayed
            elif key == ord('t'):
                if self.showThresh:
                    self.showThresh = 0
                    try:
                        cv2.destroyWindow('Thresh')
                    except:
                        pass
                else:
                    self.showThresh = 1

            # toggles Delta image displayed
            elif key == ord('d'):
                if self.showDelta:
                    self.showDelta = 0
                    try:
                        cv2.destroyWindow('Delta')
                    except:
                        pass
                else:
                    self.showDelta = 1
                    
            # toggles threshErosion image displayed
            elif key == ord('e'):
                if self.showThreshErosion:
                    self.showThreshErosion = 0
                    try:
                        cv2.destroyWindow('Thresh Erosion')
                    except: 
                        pass
                else:
                    self.showThreshErosion = 1

            # keys for Contour settings
            elif key == ord('='):
                self.contourAreaValue += 1
                print("Contour Area:{}".format(self.contourAreaValue))
            elif key == ord('-'):
                if self.contourAreaValue >= 5:
                    self.contourAreaValue -= 5
                    print("Contour Area:{}".format(self.contourAreaValue))

            # keys for thresh settings
            elif key == ord(']'):
                self.thresholdValue += 1
                print("Thresh:{}".format(self.thresholdValue))
            elif key == ord('['):
                if self.thresholdValue >= 1:
                    self.thresholdValue -= 1
                    print("Thresh:{}".format(self.thresholdValue))

            # keys for kernel
            elif key == ord('i'):
                self.kernelValue += 1
                print("Kernel:{}".format(self.kernelValue))

            elif key == ord('k'):
                # negative dimensions not allowed
                if self.kernelValue != 0:
                    self.kernelValue -= 1
                    print("Kernel:{}".format(self.kernelValue))

            elif key == ord('p'):
                print("\nContour Area:{}\nThreshold:{}\nKernel:{}".format(self.contourAreaValue, self.thresholdValue,self.kernelValue))

            elif key == ord('f'):
                if self.imageFilterToggle == 0:
                    self.imageFilterToggle = 1
                    print(f"Filters {self.imageFilterToggle}")
                else:
                    self.imageFilterToggle = 0
                    print(f"Filters {self.imageFilterToggle}")

            # Prints brightness value of current single frame
            elif key == ord('b'):
                print("Frame Average Brightness:{}".format(self.findBrightness(frame)))

            # moving frames ROI up down right left
            # move top
            elif key == ord('8'):
                pass
            # bottom
            elif key == ord('2'):
                pass
            # right
            elif key == ord('4'):
                pass
            # left
            elif key == ord('6'):
                pass


def view_all():
    pass

def main():
    cams = CamSettings.CAM_ADDRESSES
    # Prints the list of cams and it's corresponding index number
    for frame,key in enumerate(cams.keys()):
        print(f"{frame} {key} {cams[key]}")

#    # Get camara number
#    while 1:
#        try:
#            answer = int(input("Choose Camera:\n"))
#            break
#        except Exception as e:
#            print("Not a number\n{}".format(e))
#
    answer = 0
    if answer == 'All':
        cams['All']()
    else:
        for frame, key in enumerate(cams.keys()):
            if frame == answer:
                answer = key
                print(answer)
                break
        # runs the choses camara
        cam = Camara_obj(answer, cams[answer])
        cam.run_thread()
main()
