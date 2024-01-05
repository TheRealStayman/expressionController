import cv2
import mediapipe as mp
from pynput.keyboard import Key, Controller


class Hand:
    def __init__(self, image, hand, mp_hands, results, landmarks):
        self.mesh = HandMesh(image, hand, mp_hands, results, landmarks)
        self.__finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
        self.__thumb_Coord = (4, 2)

        # Use hands to find landmarks
        self.landmarks = self.mesh.landmarks
        self.results = self.mesh.results
        self.firstHandInstance = True

        # self.image = image
        self.hand = hand
        self.hand_type = self.get_type()

    def is_new(self):
        return self.firstHandInstance

    def draw(self):
        self.mesh.draw()

    def get_type(self):
        return self.mesh.get_type()

    def get_fingers_up(self):
        # Finger Counter Processor
        upCount = 0
        for coordinate in self.__finger_Coord:
            if self.mesh.hand_list[coordinate[0]][1] < self.mesh.hand_list[coordinate[1]][1]:
                upCount += 1
        return upCount

    def get_action(self):
        pass


class HandMesh:
    def __init__(self, image, hand, mp_hands, results, landmarks):
        self.mp_hands = mp_hands
        #self.hands = self.mp_hands.Hands()

        self.hand = hand

        # Use hands to find landmarks
        self.results = results
        self.landmarks = landmarks

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.image = image

        self.hand_list = []

        self.show_wireframe = True

    def draw(self):
        # Draw hand
        if self.show_wireframe:
            self.mp_drawing.draw_landmarks(self.image, self.hand, self.mp_hands.HAND_CONNECTIONS)
        for idx, lm in enumerate(self.hand.landmark):
            h, w, c = self.image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            self.hand_list.append((cx, cy))
            if self.show_wireframe:
                for point in self.hand_list:
                    cv2.circle(img=self.image, center=point, radius=3, color=(0, 255, 0), thickness=-1)

    def get_type(self):
        # Check if the hand processed is a left hand or a right hand
        hand_index = self.landmarks.index(self.hand)
        hand_label = self.results.multi_handedness[hand_index].classification[0].label
        # handType is 1 if left and 2 if right hand
        hand_type = 0
        if hand_label == "Left":
            hand_type = 1
        elif hand_label == "Right":
            hand_type = 2
        return hand_type
