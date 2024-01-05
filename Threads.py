import os
import sys
import winsound

import cv2
import mediapipe as mp
from PySide6 import QtGui
from PySide6.QtCore import Qt, QThread, Signal, Slot, QUrl
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget)
from PIL import Image
from playsound import playsound
from pynput.keyboard import KeyCode

from Calibration import Calibration
from Face import *
from Hand import *
from ImageProcessor import overlay_image_alpha


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

AImageSources = [resource_path('Input Icons for Face Controller/A_dark_light.png'),
                 resource_path('Input Icons for Face Controller/A_light_dark.png')]
BImageSources = [resource_path('Input Icons for Face Controller/B_dark_light.png'),
                 resource_path('Input Icons for Face Controller/B_light_dark.png')]
LBImageSources = [resource_path('Input Icons for Face Controller/LB_dark.png'),
                  resource_path('Input Icons for Face Controller/LB_light.png')]
RBImageSources = [resource_path('Input Icons for Face Controller/RB_dark.png'),
                  resource_path('Input Icons for Face Controller/RB_light.png')]
StartImageSources = [resource_path('Input Icons for Face Controller/Menu_dark.png'),
                     resource_path('Input Icons for Face Controller/Menu_light.png')]
SelectImageSources = [resource_path('Input Icons for Face Controller/View_dark.png'),
                      resource_path('Input Icons for Face Controller/View_light.png')]
DPadImageSources = [resource_path('Input Icons for Face Controller/Digipad_dark.png'),
                    resource_path('Input Icons for Face Controller/Digipad_up_dark.png'),
                    resource_path('Input Icons for Face Controller/Digipad_down_dark.png'),
                    resource_path('Input Icons for Face Controller/Digipad_left_dark.png'),
                    resource_path('Input Icons for Face Controller/Digipad_right_dark.png')]

size = 40, 40
DPadSize = size[0] + 20, size[1] + 20
startSelectSize = int(size[0]/2), int(size[1]/2)
ANeutral = Image.open(AImageSources[0])
ANeutral.thumbnail(size, Image.Resampling.LANCZOS)
APressed = Image.open(AImageSources[1])
APressed.thumbnail(size, Image.Resampling.LANCZOS)
BNeutral = Image.open(BImageSources[0])
BNeutral.thumbnail(size, Image.Resampling.LANCZOS)
BPressed = Image.open(BImageSources[1])
BPressed.thumbnail(size, Image.Resampling.LANCZOS)
LBNeutral = Image.open(LBImageSources[0])
LBNeutral.thumbnail(size, Image.Resampling.LANCZOS)
LBPressed = Image.open(LBImageSources[1])
LBPressed.thumbnail(size, Image.Resampling.LANCZOS)
RBNeutral = Image.open(RBImageSources[0])
RBNeutral.thumbnail(size, Image.Resampling.LANCZOS)
RBPressed = Image.open(RBImageSources[1])
RBPressed.thumbnail(size, Image.Resampling.LANCZOS)
StartNeutral = Image.open(StartImageSources[0])
StartNeutral.thumbnail(startSelectSize, Image.Resampling.LANCZOS)
StartPressed = Image.open(StartImageSources[1])
StartPressed.thumbnail(startSelectSize, Image.Resampling.LANCZOS)
SelectNeutral = Image.open(SelectImageSources[0])
SelectNeutral.thumbnail(startSelectSize, Image.Resampling.LANCZOS)
SelectPressed = Image.open(SelectImageSources[1])
SelectPressed.thumbnail(startSelectSize, Image.Resampling.LANCZOS)
DPadNeutral = Image.open(DPadImageSources[0])
DPadNeutral.thumbnail(DPadSize, Image.Resampling.LANCZOS)
DPadUp = Image.open(DPadImageSources[1])
DPadUp.thumbnail(DPadSize, Image.Resampling.LANCZOS)
DPadDown = Image.open(DPadImageSources[2])
DPadDown.thumbnail(DPadSize, Image.Resampling.LANCZOS)
DPadLeft = Image.open(DPadImageSources[3])
DPadLeft.thumbnail(DPadSize, Image.Resampling.LANCZOS)
DPadRight = Image.open(DPadImageSources[4])
DPadRight.thumbnail(DPadSize, Image.Resampling.LANCZOS)


class CameraThread(QThread):
    updateFrame = Signal(QImage)

    def __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.status = True
        self.cap = True
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_Hands = mp.solutions.hands
        self.hands = self.mp_Hands.Hands()
        self.keyboard = Controller()
        self.time = 0
        self.cal = Calibration(self.time)
        self.calibration_is_on = False

        self.up_threshold = 0
        self.down_threshold = 0
        self.l_threshold = 0
        self.r_threshold = 0
        self.thresholds = [self.up_threshold, self.down_threshold, self.l_threshold, self.r_threshold]

        self.up_key = 87
        self.down_key = 83
        self.left_key = 65
        self.right_key = 68
        self.one_right_key = 75
        self.two_right_key = 13
        self.three_right_key = 73
        self.one_left_key = 76
        self.two_left_key = 8
        self.three_left_key = 79

        self.inputs_are_disabled = False
        self.show_wireframes = True

        self.a_alpha_mask = np.array(ANeutral)[:, :, 3] / 255.0
        self.a_img_overlay = np.array(ANeutral)[:, :, :3]
        self.b_alpha_mask = np.array(BNeutral)[:, :, 3] / 255.0
        self.b_img_overlay = np.array(BNeutral)[:, :, :3]
        self.lb_alpha_mask = np.array(LBNeutral)[:, :, 3] / 255.0
        self.lb_img_overlay = np.array(LBNeutral)[:, :, :3]
        self.rb_alpha_mask = np.array(RBNeutral)[:, :, 3] / 255.0
        self.rb_img_overlay = np.array(RBNeutral)[:, :, :3]
        self.start_alpha_mask = np.array(StartNeutral)[:, :, 3] / 255.0
        self.start_img_overlay = np.array(StartNeutral)[:, :, :3]
        self.select_alpha_mask = np.array(SelectNeutral)[:, :, 3] / 255.0
        self.select_img_overlay = np.array(SelectNeutral)[:, :, :3]
        self.DPad_alpha_mask = np.array(DPadNeutral)[:, :, 3] / 255.0
        self.DPad_img_overlay = np.array(DPadNeutral)[:, :, :3]

    def run(self):
        delta_count = [0, 0]  # 0 is right, 1 is left
        delta_face_output = -1
        time_since_last_hand_input = [0, 0]  # 0 is right, 1 is left
        time_since_last_face_input = 0
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = ""
        font_scale = 1
        font_color = (255, 255, 255)
        thickness = 5
        line_type = 2
        font_color2 = (0, 0, 0)
        thickness2 = 2
        bottom_left_corner_of_text = (0, 0)
        self.cap = cv2.VideoCapture(0)
        with self.mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as face_mesh:
            while self.status:
                success, image = self.cap.read()
                if not success:
                    #print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_results = face_mesh.process(image)

                # Draw the face mesh annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                if face_results.multi_face_landmarks:
                    face_output = -1
                    for face_landmarks in face_results.multi_face_landmarks:
                        face = Face(image, face_landmarks, self.thresholds)
                        face.mesh.show_wireframe = self.show_wireframes
                        face.draw()

                        self.cal.set_face(face)

                        if self.calibration_is_on:
                            bottom_left_corner_of_text = self.cal.get_text_pos()
                            text = self.cal.get_text()

                            self.cal.calibrate()

                            self.time = self.cal.get_time() + 1

                        self.calibration_is_on = self.cal.is_running()
                        face = self.cal.get_face()

                        face_output = face.process.get_output()

                    if not self.inputs_are_disabled:
                        if face_output != delta_face_output:
                            if face_output == 0:
                                self.face_controller_processor(face_output, self.keyboard)
                            else:
                                if time_since_last_face_input > 5:
                                    self.face_controller_processor(face_output, self.keyboard)
                                    time_since_last_face_input = 0

                    time_since_last_face_input += 1
                    delta_face_output = face_output
                else:
                    delta_face_output = -1
                    time_since_last_face_input = 0

                # Use hands to find landmarks
                hand_results = self.hands.process(image)
                hand_landmarks = hand_results.multi_hand_landmarks

                if hand_landmarks:
                    count = [0, 0]  # 0 is right, 1 is left
                    for h in hand_landmarks:
                        hand = Hand(image, h, self.mp_Hands, hand_results, hand_landmarks)
                        hand.mesh.show_wireframe = self.show_wireframes
                        hand.draw()

                        hand_type = hand.get_type()
                        if hand_type == 1:
                            count[0] += hand.get_fingers_up()
                        elif hand_type == 2:
                            count[1] += hand.get_fingers_up()

                    if not self.inputs_are_disabled:
                        if count[0] != delta_count[0]:
                            if count[0] == 0:
                                self.right_hand_processor(count[0], self.keyboard)
                            if time_since_last_hand_input[0] > 5:
                                self.right_hand_processor(count[0], self.keyboard)
                                time_since_last_hand_input[0] = 0
                        elif count[1] != delta_count[1]:
                            if count[1] == 0:
                                self.left_hand_processor(count[1], self.keyboard)
                            if time_since_last_hand_input[1] > 5:
                                self.left_hand_processor(count[1], self.keyboard)
                                time_since_last_hand_input[1] = 0

                    time_since_last_hand_input[0] += 1
                    time_since_last_hand_input[1] += 1

                    delta_count[0] = count[0]
                    delta_count[1] = count[1]
                else:
                    delta_count = [0, 0]  # 0 is right, 1 is left
                    time_since_last_hand_input = [0, 0]  # 0 is right, 1 is left

                image = cv2.flip(image, 1)

                # Perform blending
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)

                img_result = np.array(image)[:, :, :3].copy()
                overlay_image_alpha(img_result, self.DPad_img_overlay, (640 - ((DPadSize[0] + 10)+(size[0]*2)+int((startSelectSize[0] + 10)*2.5))), (480 - (DPadSize[0] + 10)), self.DPad_alpha_mask)
                overlay_image_alpha(img_result, self.lb_img_overlay, (640 - (((startSelectSize[0] + 10)*2)+int(size[0]*2.25))), (480 - (size[0]*2 + 10)), self.lb_alpha_mask)
                overlay_image_alpha(img_result, self.rb_img_overlay, (640 - ((startSelectSize[0] + 10)+int(size[0]*1.25))), (480 - (size[0]*2 + 10)), self.rb_alpha_mask)
                overlay_image_alpha(img_result, self.select_img_overlay, (640 - (((startSelectSize[0] + 10)*2)+(int(size[0]*2.5)))), (480 - (startSelectSize[0] + 10)), self.select_alpha_mask)
                overlay_image_alpha(img_result, self.start_img_overlay, (640 - ((startSelectSize[0] + 10)+(int(size[0]*2.5)))), (480 - (startSelectSize[0] + 10)), self.start_alpha_mask)
                overlay_image_alpha(img_result, self.a_img_overlay, (640 - ((size[0] + 10)*2)), (480 - (size[0] + 10)), self.a_alpha_mask)
                overlay_image_alpha(img_result, self.b_img_overlay, (640 - ((size[0] + 10)*1)), (480 - (size[0] + 10)), self.b_alpha_mask)

                image = img_result[:, :, ::-1].copy()

                # Write some Text
                cv2.putText(image, text,
                            bottom_left_corner_of_text,
                            font,
                            font_scale,
                            font_color,
                            thickness,
                            line_type)
                cv2.putText(image, text,
                            bottom_left_corner_of_text,
                            font,
                            font_scale,
                            font_color2,
                            thickness2,
                            line_type)

                # Creating and scaling QImage
                h, w, ch = image.shape
                img = QImage(image.data, w, h, ch * w, QImage.Format_BGR888)
                scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)

                # Emit signal
                self.updateFrame.emit(scaled_img)
            sys.exit(-1)

    def right_hand_processor(self, count, keyboard):
        if count == 1:
            # keyboard.press('l')  # Press the A button
            keyboard.press(KeyCode.from_vk(self.one_right_key))
            print("A")
            self.a_alpha_mask = np.array(APressed)[:, :, 3] / 255.0
            self.a_img_overlay = np.array(APressed)[:, :, :3]
        elif count != 1:
            # keyboard.release('l')
            keyboard.release(KeyCode.from_vk(self.one_right_key))
            self.a_alpha_mask = np.array(ANeutral)[:, :, 3] / 255.0
            self.a_img_overlay = np.array(ANeutral)[:, :, :3]
        if count == 2:
            # keyboard.press(Key.enter)  # Press the Start button
            keyboard.press(KeyCode.from_vk(self.two_right_key))
            print("Start")
            self.start_alpha_mask = np.array(StartPressed)[:, :, 3] / 255.0
            self.start_img_overlay = np.array(StartPressed)[:, :, :3]
        elif count != 2:
            # keyboard.release(Key.enter)
            keyboard.release(KeyCode.from_vk(self.two_right_key))
            self.start_alpha_mask = np.array(StartNeutral)[:, :, 3] / 255.0
            self.start_img_overlay = np.array(StartNeutral)[:, :, :3]
        if count == 3:
            # keyboard.press('o')  # Press the Right Bumper
            keyboard.press(KeyCode.from_vk(self.three_right_key))
            print("Right Bumper")
            self.rb_alpha_mask = np.array(RBPressed)[:, :, 3] / 255.0
            self.rb_img_overlay = np.array(RBPressed)[:, :, :3]
        elif count != 3:
            # keyboard.release('o')
            keyboard.release(KeyCode.from_vk(self.three_right_key))
            self.rb_alpha_mask = np.array(RBNeutral)[:, :, 3] / 255.0
            self.rb_img_overlay = np.array(RBNeutral)[:, :, :3]

    def left_hand_processor(self, count, keyboard):
        if count == 1:
            # keyboard.press('k')  # Press the B button
            keyboard.press(KeyCode.from_vk(self.one_left_key))
            print("B")
            self.b_alpha_mask = np.array(BPressed)[:, :, 3] / 255.0
            self.b_img_overlay = np.array(BPressed)[:, :, :3]
        elif count != 1:
            # keyboard.release('k')
            keyboard.release(KeyCode.from_vk(self.one_left_key))
            self.b_alpha_mask = np.array(BNeutral)[:, :, 3] / 255.0
            self.b_img_overlay = np.array(BNeutral)[:, :, :3]
        if count == 2:
            # keyboard.press(Key.backspace)  # Press the Select button
            keyboard.press(KeyCode.from_vk(self.two_left_key))
            print("Select")
            self.select_alpha_mask = np.array(SelectPressed)[:, :, 3] / 255.0
            self.select_img_overlay = np.array(SelectPressed)[:, :, :3]
        elif count != 2:
            # keyboard.release(Key.backspace)
            keyboard.release(KeyCode.from_vk(self.two_left_key))
            self.select_alpha_mask = np.array(SelectNeutral)[:, :, 3] / 255.0
            self.select_img_overlay = np.array(SelectNeutral)[:, :, :3]
        if count == 3:
            # keyboard.press('I')  # Press the Left Bumper
            keyboard.press(KeyCode.from_vk(self.three_left_key))
            print("Left Bumper")
            self.lb_alpha_mask = np.array(LBPressed)[:, :, 3] / 255.0
            self.lb_img_overlay = np.array(LBPressed)[:, :, :3]
            winsound.PlaySound('Dramatic Vine⧸Instagram Boom - Sound Effect (HD).wav', winsound.SND_ASYNC)
        elif count != 3:
            # keyboard.release('I')
            keyboard.release(KeyCode.from_vk(self.three_left_key))
            self.lb_alpha_mask = np.array(LBNeutral)[:, :, 3] / 255.0
            self.lb_img_overlay = np.array(LBNeutral)[:, :, :3]

    def face_controller_processor(self, output, keyboard):
        if output == 1:
            print("up")  # Press up on the d-pad
            # keyboard.press('w')
            keyboard.press(KeyCode.from_vk(self.up_key))
            self.DPad_alpha_mask = np.array(DPadUp)[:, :, 3] / 255.0
            self.DPad_img_overlay = np.array(DPadUp)[:, :, :3]
        elif output != 1:
            # keyboard.release('w')
            keyboard.release(KeyCode.from_vk(self.up_key))
        if output == 2:
            print("down")  # Press down on the d-pad
            # keyboard.press('s')
            keyboard.press(KeyCode.from_vk(self.down_key))
            self.DPad_alpha_mask = np.array(DPadDown)[:, :, 3] / 255.0
            self.DPad_img_overlay = np.array(DPadDown)[:, :, :3]
        elif output != 2:
            # keyboard.release('s')
            keyboard.release(KeyCode.from_vk(self.down_key))
        if output == 3:
            print("right")  # Press right on the d-pad
            # keyboard.press('d')
            keyboard.press(KeyCode.from_vk(self.right_key))
            self.DPad_alpha_mask = np.array(DPadRight)[:, :, 3] / 255.0
            self.DPad_img_overlay = np.array(DPadRight)[:, :, :3]
        elif output != 3:
            # keyboard.release('d')
            keyboard.release(KeyCode.from_vk(self.right_key))
        if output == 4:
            #boom.play()

            print("left")  # Press left of the d-pad
            # keyboard.press('a')
            keyboard.press(KeyCode.from_vk(self.left_key))
            self.DPad_alpha_mask = np.array(DPadLeft)[:, :, 3] / 255.0
            self.DPad_img_overlay = np.array(DPadLeft)[:, :, :3]
        elif output != 4:
            # keyboard.release('a')
            keyboard.release(KeyCode.from_vk(self.left_key))
        if output == 0:
            self.DPad_alpha_mask = np.array(DPadNeutral)[:, :, 3] / 255.0
            self.DPad_img_overlay = np.array(DPadNeutral)[:, :, :3]


def toggle_cal(cal_is_on):
    cal_is_on = not cal_is_on
    return cal_is_on
