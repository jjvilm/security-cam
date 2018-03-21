#!/usr/bin/python2
import cv2
import os
import time
import commands
import moddb
from Camara import save_folder_path as save_folder


class Rff():
    # Folder name used to read images from 
    img_folder = save_folder
    # switch to iterate to equal frame n 
    switch = False
    #  controls speed of frames
    frame_speed = 0.30 # .3 normilizes time
    # global variable for max frames
    t_n_frames = 0 
    new_frame_from_slider = False
    frame_selected = 0
    # exit switch for empty directory
    stop = False

    def __init__(self):
        # sets t_n_frames 
        #self.get_dir_size(self.img_folder)
        # keeps track of the current frame loaded on display 
        self.current_frame_counter = 0
        self.loaded_frame_list = []
        self.paths = moddb.db()

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

    
    def get_dir_size(self, start_path):
        def empty_dir():
            # exit if directory is empty
            if folder_size < 0:
                self.stop = True


            #creates above folder if it does not exist
            if not os.path.exists(self.img_folder):
                print('{} created!'.format(self.img_folder))
                os.makedirs(self.img_folder)



        self.new_frame_from_slider = False

        total_size = 0
        counter = 0 

        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
                counter += 1

        if total_size <= 0:
            self.stop = True
            print("Folder empty!")
            return True


        folder_size_in_mb = (total_size/1024.0)/1024.0
        folder_size_in_gb = ((total_size/1024.0)/1024.0) /1024.0
        

        # gb
        if folder_size_in_mb >= 1024.0:
            print("Size of directory: {:.2f}GB".format(folder_size_in_gb))
        # MB
        else:
            print("Size of directory: {:.2f}MB".format(folder_size_in_mb))


        return False


    def frame_selection(self):
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

    def frame_slider(self, x):
        c_frame = cv2.getTrackbarPos('Frames:', 'Frames-Control')
        self.frame_selected = c_frame
        self.new_frame_from_slider = True
        self.switch = True

    def set_frame_speed(self, x):
        slider_speed = cv2.getTrackbarPos('Speed','Frames-Control')
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
                file_name = file_path.rfind('/')
                file_name = file_path[file_name:]
                i = save_folder + file_name

                frame = cv2.imread(i)
                print(current_frame_n, str(file_name))
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
        self.t_n_frames = self.i_yield_path('')
        print(self.t_n_frames)
        # does not run main if folder is empty size is <= 0
        if self.stop:
            return

        # window for slider
        #cv2.namedWindow('Frames-Control')
        # Slider for frame tuning
        #cv2.createTrackbar('Frames:', 'Frames-Control', 0, len(loaded_frame_list)-1,frame_slider)
        # Speed slider
        #cv2.createTrackbar('Speed','Frames-Control',0,10, set_frame_speed)

        print("Total Frames: {}".format(self.t_n_frames))
        self.display_controls()
        raw_input()

        while True:
            if self.frame_selected < 0:
                self.frame_selected = 1
            #print('Frame_selected = {}'.format(frame_selected))

            #for n_current_frame,img_path in enumerate(self.loaded_frame_list):
            for n_current_frame,img_path in self.paths.yield_paths():
                path = img_path.rfind('/')
                path = img_path[path:]
                i = save_folder + path


                self.current_frame_counter = n_current_frame
                # returns to current frame when returning from frame by frame funciton
                if n_current_frame < self.frame_selected:
                    continue
                #print(n_current_frame)
                # i is the image_file_name 
                #print(i, self.frame_selected, n_current_frame)
                # reverts back to original with same frame
               # Outputs frame to terminal
                #print("Curr: {} Sel: {}".format(n_current_frame, self.frame_selected))
                #print("Frame:{} ".format(n_current_frame))

                # if slider turns on switch then skip till new frame
                if self.switch:
                    if n_current_frame == self.frame_selected:
                        self.switch = False
                    else:
                        continue
                # Sometimes imshow crashes on this line while 
                # reading image file
                try:
                    frame = cv2.imread(i, -1)
                    cv2.imshow("Frames",frame)
                except Exception as e:
                    print(e,'\nBAD Frame')
                    continue

                

                print(self.current_frame_counter) 

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
                    print("Max frame == {}".format(len(self.loaded_frame_list) -1))
                    self.frame_selected = self.frame_selection()
                    raw_input("Press Enter to display and continue")
                    break
                # Frame by frame paused
                if key == ord('.'):
                    #self.frame_selected = self.frame_by_frame(self.frame_selected)
                    # goes into a loop that pauses frames
                    self.frame_selected = self.frame_by_frame(n_current_frame)
                    break
                # skips by 100 frames
                if key == ord('='):
                        self.frame_selected = n_current_frame + 100 
                        break
                # backwards by 100 frames
                if key == ord('-'):
                    self.frame_selected = n_current_frame - 100 
                    break

                if key == ord('b'):
                    print("Brightness value={}".format(self.findBrightness(frame)))

                #print("Frame speed: {}".format(frame_speed))
                time.sleep(self.frame_speed)
                if self.new_frame_from_slider:
                    #new_frame_from_slider = False
                    break
            else:
                # frames end here so restart loop
                print('Looping...')
                self.frame_selected = 0

    def display_controls(self):
        print("[-] & [=] Incrase frames by 200 and decrease by 100\n[.] FramebyFrame\n[/] exit FramebyFrame\n[q] Quit")

    def database_view(self):
        import moddb
        paths = moddb.db()
        for i,img in paths.yield_paths():
            print(i)
            img = str(img)
            path = img.rfind('/')
            path = img[path:]
            path = save_folder + path

            img = cv2.imread(path)
            cv2.imshow('img', img)
            cv2.waitKey(0)



if __name__ == "__main__":
    view = Rff()
    view.main()
    #view.database_view()

