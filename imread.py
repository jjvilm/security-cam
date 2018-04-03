#!/usr/bin/python2
import requests
import cv2
import os
import time
from datetime import datetime
import commands
import moddb
from CamSettings import SAVE_PATH


class Rff():
    def __init__(self):
        # get name of current day
        self.set_day = datetime.now().strftime("%A")
        # initiate databse object
        self.paths = moddb.db()
        # loads all rows into a list of tuples
        self.rows = self.paths.get_rows(self.set_day)
        # total number of frames
        self.t_n_frames = len(self.rows)
        # keeps track of current frame globaly
        self.frame_selected = 0
        # speed at which frames are displayed
        self.frame_speed = 0.095
        # value used by - + buttons
        self.frame_advance = 25
        # skip play 
        self.frame_step = 0
        # stops from getting yesterdays frames if loop is on
        self.day_loop = True
        # stats new loop based on new frame selected
        self.new_frame_from_slider = None
        # font displayed on image
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def create_window_settings(self):
        # window for slider
        cv2.namedWindow('Controls')
        # Slider for frame tuning
        cv2.createTrackbar('Frames:', 'Controls', 0, self.t_n_frames, self.frame_slider)
        # Speed slider
        cv2.createTrackbar('Speed:','Controls',0,10, self.set_frame_speed)

    def next_day(self, day):
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        day_index = days.index(self.set_day)
        if day == 'yesterday':
            new_day = day_index - 1
            # loops back to Sunday if on Monday
            if new_day == -1:
                new_day = 6
            self.update_day(days[new_day])
        else:
            tomorrow = day_index + 1
            # moves forward if on Saturday
            if tomorrow == 7:
                tomorrow = 0
            self.update_day(days[tomorrow])


    def update_day(self, day):
        """ New iteration of day starts so all varibles should reset accordingly """
        self.frame_selected = 0
        self.set_day = day
        self.rows = self.paths.get_rows(self.set_day)
        self.t_n_frames = len(self.rows)

        cv2.destroyWindow('Controls')
        self.create_window_settings()
        # Slider for frame tuning
        #cv2.setTrackbarPos('Frames:', 'Controls', 0)


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

    def frame_selection(self):
        print("Max frame == {}".format(self.t_n_frames))
        while True:
            frame_selected = raw_input("Start frame:\n")
            if frame_selected == 'q':
                return
            try:
                frame_selected = int(frame_selected)
                if frame_selected > self.t_n_frames:
                    print('Frame out of range')
                    continue
                return frame_selected
            except:
                print("NOT AN INT\n")

    def frame_slider(self, *args, **kwargs):
        self.frame_selected = cv2.getTrackbarPos('Frames:', 'Controls')
        self.new_frame_from_slider = True

    def set_frame_speed(self, *args, **kwargs):
        slider_speed = cv2.getTrackbarPos('Speed:','Controls')
        speeds = {
                0: 1,
                1: .325,
                2: .250,
                3: .200,
                4: .150,
                5: .1,
                6: .075,
                7: .050,
                8: .025,
                9: .015,
                10: 0
                }
        self.frame_speed = speeds[slider_speed]

    def frame_by_frame(self, current_frame_n):
        # switch to dipslay image after frame number is set
        display = True
        # initialize frame to avoid crash when frame > max frames or < current frame
        frame = None
        while True:
            if display:
                file_path = self.rows[current_frame_n][0]
                i = SAVE_PATH + '/' + file_path

                frame = cv2.imread(i)
                display = False
            # resizes 400% on frame by frame
            #frame = self.resize(frame)
            cv2.putText(frame,'{}/{} {}'.format(current_frame_n, self.t_n_frames, file_path), (1,30), self.font, 0.5, (0,255,0), 1, cv2.LINE_AA)
            cv2.imshow("Frames", frame)

            key = cv2.waitKey(33) & 0xFF
            if key == ord('q'):
                exit(0)
           
            # forward
            elif key == ord('.'):
                # next frame if available
                current_frame_n += 1
                # loops back to start 
                if current_frame_n  >= self.t_n_frames:
                    current_frame_n = 0
                display = True
                continue

            # backward
            elif key == ord(','):
                current_frame_n -= 1
                # loops to last frame
                if current_frame_n < 0:
                    current_frame_n = self.t_n_frames - 1
                display = True
                continue

            elif key == ord('/'):
                return current_frame_n

    def resize(self, frame):
        r = 400.0 / frame.shape[1]
        dim = (400 , int(frame.shape[0] * r))
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized

    def main(self):
        self.create_window_settings()

        while True:
            skips = self.frame_step

            if self.frame_selected < 0:
                self.frame_selected = 0

            for loop_frame_n, img_path in enumerate(self.rows):
                # skipping frames
                if skips:
                    skips -= 1
                    continue
                else:
                    skips = self.frame_step

                img_path = img_path[0]
                # restarts count from 0 with new frame selected
                if self.new_frame_from_slider:
                    self.new_frame_from_slider = False
                    break

                # returns to current frame when returning from frame by frame funciton
                elif loop_frame_n < self.frame_selected: # catches up to current frame
                    continue

                # Sometimes imshow crashes on this line while 
                # reading image file
                try:
                    # loads image from file path
                    img_path = SAVE_PATH + '/' + img_path
                    frame = cv2.imread(img_path, -1)
                    #adding frame number as overlay
                    cv2.putText(frame,'{}/{} {}'.format(loop_frame_n, self.t_n_frames, self.set_day),(1,30), self.font, 0.5,(0,255,0),1,cv2.LINE_AA)
                    cv2.imshow("Frames",frame)
                except Exception as e:
                    print(e,'\nBAD Frame')
                    continue

                key = cv2.waitKey(33) & 0xFF
                if key == ord('q'):
                    exit(0)
                elif key == ord('p'):
                    cv2.waitKey(0)
                # Increases speed
                elif key == ord('>'):
                    if self.frame_speed != 0 and self.frame_speed >= .005:
                        self.frame_speed -= .05
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Decrases frame play
                elif key == ord('<'):
                    self.frame_speed += .05
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Normal Speed
                elif key == ord('/'):
                    self.frame_speed  = 0
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Frame selection prompt
                elif key == ord('f'): # ************
                    self.frame_selected = self.frame_selection()
                    break
                # Frame by frame paused
                elif key == ord('.'):
                    # goes into a loop that pauses frames
                    self.frame_selected = self.frame_by_frame(loop_frame_n)
                    break
                # skips by 100 frames
                elif key == ord('='):
                    if self.frame_advance + loop_frame_n < self.t_n_frames:
                        self.frame_selected = loop_frame_n + self.frame_advance
                        break
                # backwards by 100 frames
                elif key == ord('-'):
                    minus_frames = loop_frame_n - self.frame_advance
                    if minus_frames < 0:
                        self.frame_selected = self.t_n_frames - abs(minus_frames) 
                    else:
                        self.frame_selected = minus_frames
                    break

                # prints brightness value of frame to terminal
                elif key == ord('r'):
                    print("Brightness value={}".format(self.findBrightness(frame)))
                # Moves to next day
                elif key == ord('b'):
                    self.next_day('yesterday')
                    break
                elif key == ord('n'):
                    self.next_day('tomorrow')
                    break
                # toggles day loop
                elif key == ord('l'):
                    if self.day_loop:
                        print("Day Loop OFF")
                        self.day_loop = False
                    else:
                        print("Day Loop ON")
                        self.day_loop = True
                elif key == ord('s'):
                    if self.frame_step >= 0:
                        self.frame_step += 1
                        print("Frame Step:{}".format(self.frame_step))
                        continue
                elif key == ord('S'):
                    if self.frame_step >= 1:
                        self.frame_step -= 1
                        print("Frame Step:{}".format(self.frame_step))
                        continue

                #print("Frame speed: {}".format(frame_speed))
                time.sleep(self.frame_speed)

            else: # for loops successfully iterated here so it runs this w/o breaking at the end
                if self.day_loop:
                    # frames end here so restart loop
                    print('Looping...')
                    self.frame_selected = 0
                else:
                    # restart variables for smoothness
                    self.frame_selected = 0
                    self.next_day('yesterday')
                    #cv2.destroyWindow('Controls')
                    #self.create_window_settings()

    def display_controls(self):
        print("[-] & [=] Incrase frames by 200 and decrease by 100\n[.] FramebyFrame\n[/] exit FramebyFrame\n[q] Quit")


if __name__ == "__main__":
    view = Rff()
    #view.next_day()
    view.main()
    #view.debug_func()

