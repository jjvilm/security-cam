#!/usr/bin/python2
import cv2
import os
import time
import commands
import moddb
from Camara import save_folder_path as save_folder


class Rff():
    def __init__(self):
        self.paths = moddb.db()
        # total number of frames
        self.t_n_frames = self.i_yield_path('')
        self.frame_selected = 0
        self.frame_speed = 0.30
        # exit switch for empty directory
        self.stop = False
        self.new_frame_from_slider = None

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
                0: 0,
                1: .005,
                2: .015,
                3: .025,
                4: .050,
                5: .075,
                6: .1,
                7: .3,
                8: .5,
                9: .9,
                10: 1
                }
        self.frame_speed = speeds[slider_speed]
    def i_yield_path(self, frame_index):
        """Returns len of rows """
        for i, path in self.paths.yield_paths():
            if i == frame_index:
                return path
        return i

    def frame_by_frame(self, current_frame_n):
        # switch to dipslay image after frame number is set
        display = True
        # initialize frame to avoid crash when frame > max frames or < current frame
        frame = None
        while True:
            if display:
                file_path = self.i_yield_path(current_frame_n)
                i = save_folder + '/' + file_path

                frame = cv2.imread(i)
                print(current_frame_n, str(file_path))
                display = False
            # resizes 400% on frame by frame
            #frame = self.resize(frame)
            cv2.imshow("Frames", frame)

            key = cv2.waitKey(33) & 0xFF
           
            # forward
            if key == ord('.'):
                # next frame if available
                if current_frame_n  < self.t_n_frames:
                    current_frame_n += 1
                    display = True
                    continue
                # loop back to begiining
                else:
                    current_frame_n = 1
                    display = True
                    continue

            # backward
            if key == ord(','):
                if current_frame_n > 0:
                    current_frame_n -= 1
                    # go to end from beginning
                    if current_frame_n == 0:
                        current_frame_n = self.t_n_frames
                    display = True
                    continue

            if key == ord('/'):
                return current_frame_n

    def resize(self, frame):
        r = 400.0 / frame.shape[1]
        dim = (400 , int(frame.shape[0] * r))
        resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        return resized

    def main(self):
        font = font = cv2.FONT_HERSHEY_SIMPLEX
        print(self.t_n_frames)
        # does not run main if folder is empty size is <= 0
        if self.stop:
            return

        # window for slider
        cv2.namedWindow('Controls')
        # Slider for frame tuning
        cv2.createTrackbar('Frames:', 'Controls', 0, self.t_n_frames, self.frame_slider)
        # Speed slider
        cv2.createTrackbar('Speed:','Controls',0,10, self.set_frame_speed)

        #print("Total Frames: {}".format(self.t_n_frames))
        #self.display_controls()

        while True:
            if self.frame_selected < 0:
                self.frame_selected = 1

            for loop_frame_n, img_path in self.paths.yield_paths():
                # restarts count from 0 with new frame selected
                if self.new_frame_from_slider:
                    self.new_frame_from_slider = False
                    break

                # returns to current frame when returning from frame by frame funciton
                if loop_frame_n < self.frame_selected:
                    continue

                ### DEBUG slows down image read
                #cv2.setTrackbarPos('Frames:', 'Controls', loop_frame_n)
                ### DEBUG 
                # Sometimes imshow crashes on this line while 
                # reading image file
                try:
                    # loads image from file path
                    img_path = save_folder + '/' + img_path
                    frame = cv2.imread(img_path, -1)
                    #adding frame number as overlay
                    cv2.putText(frame,'{}'.format(int(loop_frame_n)),(5,50), font, 0.5,(0,255,0),1,cv2.LINE_AA)
                    cv2.imshow("Frames",frame)
                except Exception as e:
                    print(e,'\nBAD Frame')
                    continue

                key = cv2.waitKey(33) & 0xFF
                if key == ord('q'):
                    self.stop = 1
                    exit(0)
                    return
                if key == ord('p'):
                    cv2.waitKey(0)
                # Increases speed
                if key == ord('>'):
                    if self.frame_speed != 0 and self.frame_speed >= .005:
                        self.frame_speed -= .05
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Decrases frame play
                if key == ord('<'):
                    self.frame_speed += .05
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Normal Speed
                if key == ord('/'):
                    self.frame_speed  = 0
                    print('Frame speed changed to {}'.format(self.frame_speed))
                # Frame selection prompt
                if key == ord('f'): # ************
                    self.frame_selected = self.frame_selection()
                    break
                # Frame by frame paused
                if key == ord('.'):
                    # goes into a loop that pauses frames
                    self.frame_selected = self.frame_by_frame(loop_frame_n)
                    break
                # skips by 100 frames
                if key == ord('='):
                        self.frame_selected = loop_frame_n + 100 
                        break
                # backwards by 100 frames
                if key == ord('-'):
                    self.frame_selected = loop_frame_n - 100 
                    break
                # prints brightness value of frame to terminal
                if key == ord('b'):
                    print("Brightness value={}".format(self.findBrightness(frame)))

                #print("Frame speed: {}".format(frame_speed))
                time.sleep(self.frame_speed)

            else:
                # frames end here so restart loop
                print('Looping...')
                self.frame_selected = 0

    def display_controls(self):
        print("[-] & [=] Incrase frames by 200 and decrease by 100\n[.] FramebyFrame\n[/] exit FramebyFrame\n[q] Quit")


if __name__ == "__main__":
    view = Rff()
    view.main()

