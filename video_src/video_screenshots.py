# Importing all necessary libraries
import cv2
import os
import time


# Read the video from specified path

class video_screenshots:
    def __init__(self, folder_path, delay):
        self.folder_path = folder_path
        self.delay = delay

    def main(self):
        cam = cv2.VideoCapture(self.folder_path)
        try:

            # creating a folder named data
            if not os.path.exists('video_screenshots'):
                os.makedirs('video_screenshots')

            # if not created then raise error
        except OSError:
            print('Error: Creating directory of video_screenshots')

        currentframe = 0
        fps = cam.get(cv2.CAP_PROP_FPS)
        total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps else 0

        frame_interval = int(round(self.delay * fps))
        if frame_interval <= 0:
            frame_interval = 1

        while True:
            cam.set(cv2.CAP_PROP_POS_FRAMES, currentframe)
            ret, frame = cam.read()

            if ret:
                # if video is still left continue creating images
                name = './video_screenshots/frame' + str(currentframe) + '.jpg'
                print('Creating...' + name)

                # writing the extracted images
                cv2.imwrite(name, frame)

                # increasing counter so that it will
                # show how many frames are created
                currentframe += frame_interval
            else:
                break

        # Release all space and windows once done
        cam.release()
        cv2.destroyAllWindows()
