import cv2
import numpy as np
import statistics


class Calibration:
    def __init__(self, time):
        self.bottom_left_corner_of_text = (0, 0)
        self.text = ""

        self.neutralArray = [[0, 0, 0], [0, 0, 0],
                        [0, 0, 0]]  # [x] = upDown data, left data, right data; [y] = low value, SD, high value
        self.upArray = [0, 0, 0]  # 0 = low value, 1 = median, 2 = high value
        self.downArray = [0, 0, 0]
        self.leftArray = [0, 0, 0]
        self.rightArray = [0, 0, 0]
        self.neutralArrayData = [[], [], []]
        self.upArrayData = []
        self.downArrayData = []
        self.leftArrayData = []
        self.rightArrayData = []
        self.phase = 1
        self.time = time
        self.is_running_bool = False

        self.face = None

    def calibrate(self):
        up_down_score = self.face.process.up_down_score
        l_up_score = self.face.process.l_score
        r_up_score = self.face.process.r_score

        # Inbetween text
        if self.phase in [1, 3, 7, 11, 15, 19, 23]:
            if self.time < 75:
                self.do_phase(self.phase, up_down_score, l_up_score, r_up_score)
                self.time += 1
            else:
                self.time = 0
                self.phase += 1

        # Calibration text
        if self.phase in [5, 9, 13, 17, 21, 25]:
            if self.time < 150:
                self.do_phase(self.phase, up_down_score, l_up_score, r_up_score)
                self.time += 1
            else:
                self.time = 0
                self.phase += 1

        # Breaks
        if self.phase in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 26]:
            if self.time < 15:
                self.do_phase(self.phase, up_down_score, l_up_score, r_up_score)
                self.time += 1
            elif self.phase == 26:
                self.phase = 1
                self.time = 0
                self.turn_off()
            else:
                self.time = 0
                self.phase += 1

        # Set Threshold Values
        if self.phase == 24:
            if self.time < 1:
                self.do_phase(self.phase, up_down_score, l_up_score, r_up_score)
                self.time += 1
            else:
                self.time = 0
                self.phase += 1

    def get_face(self):
        return self.face

    def set_face(self, f):
        self.face = f

    def set_time(self, t):
        self.time = t

    def get_time(self):
        return self.time

    def get_text(self):
        return self.text

    def get_text_pos(self):
        return self.bottom_left_corner_of_text

    def is_running(self):
        return self.is_running_bool

    def turn_on(self):
        self.is_running_bool = True

    def turn_off(self):
        self.is_running_bool = False

    def do_phase(self, number, up_down_score, l_up_score, r_up_score):
        # In between text
        if number == 1:
            self.bottom_left_corner_of_text = (250, 450)
            self.text = "Welcome!"
        elif number == 3:
            self.bottom_left_corner_of_text = (150, 450)
            self.text = "Let's get calibrated..."
        elif number in [7, 11, 15, 19, 23]:
            self.bottom_left_corner_of_text = (250, 450)
            self.text = "Good"

        # Callibration text
        if number == 5:
            self.bottom_left_corner_of_text = (200, 450)
            self.text = "Relax your face"
            self.neutralArrayData[0].append(up_down_score)
            self.neutralArrayData[1].append(l_up_score)
            self.neutralArrayData[2].append(r_up_score)
        elif number == 9:
            self.bottom_left_corner_of_text = (150, 450)
            self.text = "Raise both eyebrows"
            self.upArrayData.append(up_down_score)
        elif number == 13:
            self.bottom_left_corner_of_text = (150, 450)
            self.text = "Furrow your eyebrows"
            self.downArrayData.append(up_down_score)
        elif number == 17:
            self.rightArrayData.append(r_up_score)
            self.bottom_left_corner_of_text = (125, 450)
            self.text = "Raise your right eyebrow"
        elif number == 21:
            self.leftArrayData.append(l_up_score)
            self.bottom_left_corner_of_text = (125, 450)
            self.text = "Raise your left eyebrow"
        elif number == 25:
            self.bottom_left_corner_of_text = (150, 450)
            #print(self.face.process.get_threshold(0))
            if self.face.process.get_threshold(0) != 0:
                self.text = "Calibration complete"
                #print("Calibration complete")
            else:
                self.text = "Calibration failed"
                #print("Calibration failed")

        # Breaks
        if number in [2, 4, 8, 12, 16, 20, 26]:
            self.text = ""
        elif number == 6:
            self.neutralArrayData[0].sort()
            self.neutralArrayData[1].sort()
            self.neutralArrayData[2].sort()
            self.neutralArray[0][0] = self.neutralArrayData[0][0]  # upDownScore low number
            self.neutralArray[0][1] = statistics.median(self.neutralArrayData[0])  # upDownScore median
            self.neutralArray[0][2] = self.neutralArrayData[0][-1]  # upDownScore high number
            self.neutralArray[1][0] = self.neutralArrayData[1][0]  # lUpScore low number
            self.neutralArray[1][1] = statistics.median(self.neutralArrayData[1])  # lUpScore median
            self.neutralArray[1][2] = self.neutralArrayData[1][-1]  # lUpScore high number
            self.neutralArray[2][0] = self.neutralArrayData[2][0]  # rUpScore low number
            self.neutralArray[2][1] = statistics.median(self.neutralArrayData[2])  # rUpScore median
            self.neutralArray[2][2] = self.neutralArrayData[2][-1]  # rUpScore high number
            self.text = ""
        elif number == 10:
            self.upArrayData.sort()
            self.upArray[0] = np.percentile(self.upArrayData, 25)  # upDownScore low number
            self.upArray[1] = statistics.median(self.upArrayData)  # upDownScore median
            self.upArray[2] = np.percentile(self.upArrayData, 80)  # upDownScore high number
            self.text = ""
        elif number == 14:
            self.downArrayData.sort()
            self.downArray[0] = np.percentile(self.downArrayData, 35)  # upDownScore low number
            self.downArray[1] = statistics.median(self.downArrayData)  # upDownScore median
            self.downArray[2] = np.percentile(self.downArrayData, 75)  # upDownScore high number
            self.text = ""
        elif number == 18:
            self.rightArrayData.sort()
            self.rightArray[0] = np.percentile(self.rightArrayData, 25)  # rUpScore low number
            self.rightArray[1] = statistics.median(self.rightArrayData)  # rUpScore median
            self.rightArray[2] = np.percentile(self.rightArrayData, 85)  # rUpScore high number
            self.text = ""
        elif number == 22:
            self.leftArrayData.sort()
            self.leftArray[0] = np.percentile(self.leftArrayData, 25)  # lUpScore low number
            self.leftArray[1] = statistics.median(self.leftArrayData)  # lUpScore median
            self.leftArray[2] = np.percentile(self.leftArrayData, 85)  # lUpScore high number
            self.text = ""
        elif number == 24:
            if self.upArray[2] > self.neutralArray[0][1]:
                print(str(self.upArray[2]))
                print(str(self.neutralArray[0][1]))
                print("Calibration failed: Up Array")
            elif self.downArray[1] < self.neutralArray[0][1]:
                # print(str(self.downArray))
                print(str(self.downArray[0]))
                print(str(self.neutralArray[0][1]))
                print("Calibration failed: Down Array")
            elif self.rightArray[2] > self.neutralArray[2][1]:
                print("Calibration failed: Right Array")
                print(str(self.rightArray[2]))
                print(str(self.neutralArray[2][1]))
            elif self.leftArray[2] > self.neutralArray[1][1]:
                print(str(self.leftArray[2]))
                print(str(self.neutralArray[1][1]))
                print("Calibration failed: Left Array")
            else:
                self.face.process.set_threshold(0, self.get_up_threshold())
                self.face.process.set_threshold(1, self.get_down_threshold())
                self.face.process.set_threshold(2, self.get_left_threshold())
                self.face.process.set_threshold(3, self.get_right_threshold())
                print("Down: " + str(self.face.process.get_threshold(1)))
                print("Up: " + str(self.face.process.get_threshold(0)))
                print("Right: " + str(self.face.process.get_threshold(3)))
                print("Left: " + str(self.face.process.get_threshold(2)))

    def get_up_threshold(self):
        if self.upArray[2] > self.neutralArray[0][2]:
            return self.neutralArray[0][2] - 1
        else:
            return self.upArray[2]

    def get_down_threshold(self):
        if self.downArray[0] < self.neutralArray[0][0]:
            return self.neutralArray[0][0] + 1
        else:
            return self.downArray[0]

    def get_left_threshold(self):
        if self.leftArray[2] > self.neutralArray[1][2]:
            return self.neutralArray[1][2] - 3
        else:
            return self.leftArray[2]

    def get_right_threshold(self):
        if self.rightArray[2] > self.neutralArray[2][2]:
            return self.neutralArray[2][2] - 3
        else:
            return self.rightArray[2]


def end_calibration():
    is_running = False
    return is_running
