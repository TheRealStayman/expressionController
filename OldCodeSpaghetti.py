import cv2
import mediapipe as mp
import numpy as np
from pynput.keyboard import Key, Controller
import statistics

# define keyboard
keyboard = Controller()

mp_Hands = mp.solutions.hands
hands = mp_Hands.Hands()
finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_Coord = (4, 2)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


def get_facemesh_coords(landmark_list, img):
    """Extract FaceMesh landmark coordinates into 468x3 NumPy array.
    """
    alt_h, alt_w = img.shape[:2]  # grab width and height from image
    xyz = [(landmark.x, landmark.y, landmark.z) for landmark in landmark_list.landmark]

    return np.multiply(xyz, [alt_w, alt_h, alt_w]).astype(int)


# call: get_facemesh_coords(results.multi_face_landmarks[0], image)

def heron(h_a, h_b, h_c):
    s = (h_a + h_b + h_c) / 2
    area = (s * (s - h_a) * (s - h_b) * (s - h_c)) ** 0.5
    return area


def distance3d(coord1, coord2):
    x1 = coord1[0]
    x2 = coord2[0]
    y1 = coord1[1]
    y2 = coord2[1]
    z1 = coord1[2]
    z2 = coord2[2]
    a = (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
    d = a ** 0.5
    return d


def areatriangle3d(coord1, coord2, coord3):
    adist = distance3d(coord1, coord2)
    bdist = distance3d(coord2, coord3)
    cdist = distance3d(coord3, coord1)
    ares = heron(adist, bdist, cdist)
    return ares


neutralArray = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # [x] = upDown data, left data, right data; [y] = low value, SD, high value
upArray = [0, 0, 0]  # 0 = low value, 1 = median, 2 = high value
downArray = [0, 0, 0]
leftArray = [0, 0, 0]
rightArray = [0, 0, 0]
neutralArrayData = [[], [], []]
upArrayData = []
downArrayData = []
leftArrayData = []
rightArrayData = []
upThreshold = None
downThreshold = None
leftThreshold = None
rightThreshold = None

dPadOutput = 0
dPadOutputInit = -5
loopsBetween = 0

lUpCountInit = 0
rUpCountInit = 0
handTypeInit = 0
lHandLoopsBetween = 0
rHandLoopsBetween = 0
newHandCheck = 0

ignoreNeutral = False

time = 0

# For webcam input:
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
cap = cv2.VideoCapture(0)
with mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        faceResults = face_mesh.process(image)

        # Use hands to find landmarks
        handResults = hands.process(image)
        handLandmarks = handResults.multi_hand_landmarks

        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if faceResults.multi_face_landmarks:
            faceList = []
            for face_landmarks in faceResults.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_tesselation_style())
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles
                    .get_default_face_mesh_contours_style())
                # mp_drawing.draw_landmarks(
                #     image=image,
                #     landmark_list=face_landmarks,
                #     connections=mp_face_mesh.FACEMESH_IRISES,
                #     landmark_drawing_spec=None,
                #     connection_drawing_spec=mp_drawing_styles
                #     .get_default_face_mesh_iris_connections_style())

                # Collect the face landmark locations
                for idx, lm in enumerate(face_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    faceList.append((cx, cy))
                    # Put numbers in each point, used for testing purposes.
                    # itr = 0
                    # for point in faceList:
                    #     cv2.putText(image, str(itr), point, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 0)
                    #     itr += 1

                # Put all face landmarks into an array
                facemeshCoords = get_facemesh_coords(face_landmarks, image)

                # Detect how big the face is
                cntrConstArea = areatriangle3d(facemeshCoords[54], facemeshCoords[93], facemeshCoords[389])

                # The area above each eyebrow as measured by triangles
                # Left side of Face
                lEyebrowArea = (areatriangle3d(facemeshCoords[9], facemeshCoords[151], facemeshCoords[337]) +
                                areatriangle3d(facemeshCoords[9], facemeshCoords[336], facemeshCoords[337]) +
                                areatriangle3d(facemeshCoords[336], facemeshCoords[337], facemeshCoords[299]) +
                                areatriangle3d(facemeshCoords[336], facemeshCoords[299], facemeshCoords[296]) +
                                areatriangle3d(facemeshCoords[296], facemeshCoords[299], facemeshCoords[334]) +
                                areatriangle3d(facemeshCoords[299], facemeshCoords[334], facemeshCoords[333]) +
                                areatriangle3d(facemeshCoords[333], facemeshCoords[334], facemeshCoords[293]) +
                                areatriangle3d(facemeshCoords[333], facemeshCoords[298], facemeshCoords[293]) +
                                areatriangle3d(facemeshCoords[301], facemeshCoords[298], facemeshCoords[293]) -
                                areatriangle3d(facemeshCoords[8], facemeshCoords[9], facemeshCoords[285]) -
                                areatriangle3d(facemeshCoords[9], facemeshCoords[336], facemeshCoords[285]) -
                                areatriangle3d(facemeshCoords[8], facemeshCoords[417], facemeshCoords[285]))
                # Right Side of Face
                rEyebrowArea = (areatriangle3d(facemeshCoords[71], facemeshCoords[63], facemeshCoords[68]) +
                                areatriangle3d(facemeshCoords[104], facemeshCoords[63], facemeshCoords[68]) +
                                areatriangle3d(facemeshCoords[104], facemeshCoords[63], facemeshCoords[105]) +
                                areatriangle3d(facemeshCoords[105], facemeshCoords[104], facemeshCoords[69]) +
                                areatriangle3d(facemeshCoords[105], facemeshCoords[66], facemeshCoords[69]) +
                                areatriangle3d(facemeshCoords[66], facemeshCoords[69], facemeshCoords[107]) +
                                areatriangle3d(facemeshCoords[107], facemeshCoords[69], facemeshCoords[108]) +
                                areatriangle3d(facemeshCoords[107], facemeshCoords[108], facemeshCoords[9]) +
                                areatriangle3d(facemeshCoords[108], facemeshCoords[9], facemeshCoords[151]) -
                                areatriangle3d(facemeshCoords[9], facemeshCoords[107], facemeshCoords[55]) -
                                areatriangle3d(facemeshCoords[9], facemeshCoords[8], facemeshCoords[55]) -
                                areatriangle3d(facemeshCoords[193], facemeshCoords[8], facemeshCoords[55]))
                # Total area
                eyebrowArea = lEyebrowArea + rEyebrowArea

                # 36 and above is down, ~33 is neutral, 27 and below is up
                upDownScore = (eyebrowArea / cntrConstArea) * 100

                # 13.5 and below is up
                lUpScore = (lEyebrowArea / rEyebrowArea) * 10

                # Below 13.65 is up
                rUpScore = (rEyebrowArea / lEyebrowArea) * 10

                font = cv2.FONT_HERSHEY_SIMPLEX
                bottomLeftCornerOfText = (0, 0)
                fontScale = 1
                fontColor = (255, 255, 255)
                thickness = 5
                lineType = 2

                fontColor2 = (0, 0, 0)
                thickness2 = 2
                text = ""

                if 100 > time > 50:
                    bottomLeftCornerOfText = (250, 450)
                    text = "Welcome!"
                elif 250 > time > 150:
                    bottomLeftCornerOfText = (150, 450)
                    text = "Let's get calibrated..."
                elif 500 > time > 300:
                    bottomLeftCornerOfText = (200, 450)
                    text = "Relax your face"
                    neutralArrayData[0].append(upDownScore)
                    neutralArrayData[1].append(lUpScore)
                    neutralArrayData[2].append(rUpScore)
                elif 502 > time > 500:
                    neutralArrayData[0].sort()
                    neutralArrayData[1].sort()
                    neutralArrayData[2].sort()
                    neutralArray[0][0] = neutralArrayData[0][0]  # upDownScore low number
                    neutralArray[0][1] = statistics.median(neutralArrayData[0])  # upDownScore median
                    neutralArray[0][2] = neutralArrayData[0][-1]  # upDownScore high number
                    neutralArray[1][0] = neutralArrayData[1][0]  # lUpScore low number
                    neutralArray[1][1] = statistics.median(neutralArrayData[1])  # lUpScore median
                    neutralArray[1][2] = neutralArrayData[1][-1]  # lUpScore high number
                    neutralArray[2][0] = neutralArrayData[2][0]  # rUpScore low number
                    neutralArray[2][1] = statistics.median(neutralArrayData[2])  # rUpScore median
                    neutralArray[2][2] = neutralArrayData[2][-1]  # rUpScore high number
                elif 580 > time > 530:
                    bottomLeftCornerOfText = (250, 450)
                    text = "Good"
                elif 800 > time > 600:
                    bottomLeftCornerOfText = (150, 450)
                    text = "Raise both eyebrows"
                    upArrayData.append(upDownScore)
                elif 850 > time > 825:
                    upArrayData.sort()
                    upArray[0] = np.percentile(upArrayData, 25)  # upDownScore low number
                    upArray[1] = statistics.median(upArrayData)  # upDownScore median
                    upArray[2] = np.percentile(upArrayData, 75)  # upDownScore high number
                    bottomLeftCornerOfText = (250, 450)
                    text = "Good"
                elif 1075 > time > 875:
                    bottomLeftCornerOfText = (150, 450)
                    text = "Furrow your eyebrows"
                    downArrayData.append(upDownScore)
                elif 1150 > time > 1100:
                    downArrayData.sort()
                    downArray[0] = np.percentile(downArrayData, 10)  # upDownScore low number
                    downArray[1] = statistics.median(downArrayData)  # upDownScore median
                    downArray[2] = np.percentile(downArrayData, 75)  # upDownScore high number
                    bottomLeftCornerOfText = (250, 450)
                    text = "Good"
                elif 1375 > time > 1175:
                    rightArrayData.append(rUpScore)
                    bottomLeftCornerOfText = (125, 450)
                    text = "Raise your right eyebrow"
                elif 1425 > time > 1400:
                    rightArrayData.sort()
                    rightArray[0] = np.percentile(rightArrayData, 25)  # rUpScore low number
                    rightArray[1] = statistics.median(rightArrayData)  # rUpScore median
                    rightArray[2] = np.percentile(rightArrayData, 75)  # rUpScore high number
                    bottomLeftCornerOfText = (250, 450)
                    text = "Good"
                elif 1650 > time > 1450:
                    leftArrayData.append(lUpScore)
                    bottomLeftCornerOfText = (125, 450)
                    text = "Raise your left eyebrow"
                elif 1725 > time > 1675:
                    leftArrayData.sort()
                    leftArray[0] = np.percentile(leftArrayData, 25)  # lUpScore low number
                    leftArray[1] = statistics.median(leftArrayData)  # lUpScore median
                    leftArray[2] = np.percentile(leftArrayData, 75)  # lUpScore high number
                    bottomLeftCornerOfText = (250, 450)
                    text = "Good"
                elif 1728 > time > 1726:
                    if upArray[2] > neutralArray[0][1]:
                        print(str(upArray[2]))
                        print(str(neutralArray[0][1]))
                        print("Calibration failed: Up Array")
                    elif downArray[0] < neutralArray[0][1]:
                        #print(str(downArray))
                        print(str(downArray[0]))
                        print(str(neutralArray[0][1]))
                        print("Calibration failed: Down Array")
                    elif rightArray[2] > neutralArray[2][1]:
                        print("Calibration failed: Right Array")
                        print(str(rightArray[2]))
                        print(str(neutralArray[2][1]))
                    elif leftArray[2] > neutralArray[1][1]:
                        print(str(leftArray[2]))
                        print(str(neutralArray[1][1]))
                        print("Calibration failed: Left Array")
                    else:
                        # if upArray[2] < neutralArray[0][2]:
                        #     upThreshold = neutralArray[0][2] - 3
                        # else:
                        #     upThreshold = upArray[2]
                        if downArray[0] < neutralArray[0][0]:
                            print("Using neutral array")
                            downThreshold = neutralArray[0][0] + 1
                        else:
                            print("Using down array")
                            downThreshold = downArray[0]
                        if rightArray[2] < neutralArray[2][2]:
                            rightThreshold = neutralArray[2][2] - 3
                        else:
                            rightThreshold = rightArray[1]
                        if leftArray[2] < neutralArray[1][2]:
                            leftThreshold = neutralArray[1][2] - 3
                        else:
                            leftThreshold = leftArray[1]

                        #downThreshold = neutralArray[0][0] + 1
                        # downThreshold = downArray[1]
                        #leftThreshold = leftArray[1]
                        #rightThreshold = rightArray[1]
                        upThreshold = upArray[1]

                        print("Down: " + str(downThreshold))
                        print("Up: " + str(upThreshold))
                        print("Right: " + str(rightThreshold))
                        print("Left: " + str(leftThreshold))
                        #upThreshold = rightThreshold + leftThreshold
                        # if upThreshold < rightThreshold:
                        #     upThreshold = rightThreshold + 1
                        # elif upThreshold < leftThreshold:
                        #     upThreshold = leftThreshold + 1

                        #upThreshold = neutralArray[0][2] - 0.75
                        #downThreshold = neutralArray[0][0] + 0.75
                        #rightThreshold = neutralArray[2][2] - 0.75
                        #leftThreshold = neutralArray[1][2] - 0.75
                elif 2000 > time > 1775:
                    bottomLeftCornerOfText = (150, 450)
                    if upThreshold is not None:
                        text = "Calibration complete"
                    else:
                        text = "Calibration failed"

                # Write some Text
                image = cv2.flip(image, 1)
                cv2.putText(image, text,
                            bottomLeftCornerOfText,
                            font,
                            fontScale,
                            fontColor,
                            thickness,
                            lineType)
                cv2.putText(image, text,
                            bottomLeftCornerOfText,
                            font,
                            fontScale,
                            fontColor2,
                            thickness2,
                            lineType)
                image = cv2.flip(image, 1)

                # 0 is neutral, 1 is up, 2 is down, 3 is right, 4 is left
                if upThreshold is not None:
                    #print("R up: " + str(rUpScore))
                    #print("L up: " + str(lUpScore))
                    if upDownScore > downThreshold:
                        dPadOutput = 2
                    elif upDownScore < upThreshold:
                        dPadOutput = 1
                    elif rUpScore < rightThreshold:
                        dPadOutput = 3
                    elif lUpScore < leftThreshold:
                        dPadOutput = 4
                    else:
                        dPadOutput = 0

                # Process whether a new input should be activated
                if dPadOutput == dPadOutputInit:  # If there hasn't been a change in the eyebrow gesture since last loop
                    doesShow = False
                # elif dPadOutput == 0 and loopsBetween >= 3:
                #    doesShow = True
                elif loopsBetween < 7:  # If the last time a new input was activated was less than 7 loops ago
                    doesShow = False
                else:
                    doesShow = True

                # Process the eyebrow expression
                if dPadOutput == 1 and doesShow:  # If the eyebrows are up and a new input can activate
                    print("up")  # Press up on the d-pad
                    keyboard.press('w')
                    loopsBetween = 0
                elif dPadOutput != 1 and loopsBetween >= 3:
                    keyboard.release('w')
                if dPadOutput == 2 and doesShow:  # If the eyebrows are down and a new input can activate
                    print("down")  # Press down on the d-pad
                    keyboard.press('s')
                    loopsBetween = 0
                elif dPadOutput != 2 and loopsBetween >= 3:
                    keyboard.release('s')
                if dPadOutput == 3 and doesShow:  # If the right eyebrow is up and a new input can activate
                    print("right")  # Press right on the d-pad
                    keyboard.press('d')
                    loopsBetween = 0
                elif dPadOutput != 3 and loopsBetween >= 3:
                    keyboard.release('d')
                if dPadOutput == 4 and doesShow:  # If the left eyebrow is up and a new input can activate
                    print("left")  # Press left of the d-pad
                    keyboard.press('a')
                    loopsBetween = 0
                elif dPadOutput != 4 and loopsBetween >= 3:
                    keyboard.release('a')
                if dPadOutput == 0 and doesShow:  # If no expression exists
                    print("neutral")  # Unpress all inputs on the d-pad
                    loopsBetween = 0

                # Update dPadOutputInit with last loops value to compare if there has been a change
                if loopsBetween >= 6:
                    dPadOutputInit = dPadOutput

                if loopsBetween < 7:
                    loopsBetween += 1  # Update loops between last input

        # Hand Processing
        firstHandInstance = True
        if handLandmarks:
            # Check if there is a new hand on screen
            if len(handLandmarks) == newHandCheck:
                firstHandInstance = False
            else:
                firstHandInstance = True

            # Count the number of fingers in each hand
            lUpCount = 0
            rUpCount = 0
            for hand in handLandmarks:
                handList = []

                # Draw hand
                mp_drawing.draw_landmarks(image, hand, mp_Hands.HAND_CONNECTIONS)
                for idx, lm in enumerate(hand.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    handList.append((cx, cy))
                    for point in handList:
                        cv2.circle(img=image, center=point, radius=3, color=(0, 255, 0), thickness=-1)

                # Check if the hand processed is a left hand or a right hand
                handIndex = handResults.multi_hand_landmarks.index(hand)
                handLabel = handResults.multi_handedness[handIndex].classification[0].label
                # handType is 1 if left and 2 if right hand
                if handLabel == "Left":
                    handType = 1
                elif handLabel == "Right":
                    handType = 2

                # Finger Counter Processor
                for coordinate in finger_Coord:
                    if handType == 1:
                        if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                            rUpCount += 1
                    elif handType == 2:
                        if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                            lUpCount += 1

            for hand in handLandmarks:

                # Check if the hand processed is a left hand or a right hand
                handIndex = handResults.multi_hand_landmarks.index(hand)
                handLabel = handResults.multi_handedness[handIndex].classification[0].label
                # handType is 1 if left and 2 if right hand
                if handLabel == "Left":
                    handType = 1
                elif handLabel == "Right":
                    handType = 2

                # # Finger Counter Processor
                # for coordinate in finger_Coord:
                #     if handType == 1:
                #         if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                #             rUpCount += 1
                #         else:
                #             rUpCount -= 1
                #     elif handType == 2:
                #         if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                #             lUpCount += 1
                #         else:
                #             lUpCount -= 1
                # # Thumb counter processor
                # # if handType == 2:
                # #     if handList[thumb_Coord[0]][0] < handList[thumb_Coord[1]][0]:
                # #         lUpCount += 1
                # # elif handType == 1:
                # #     if handList[thumb_Coord[0]][0] > handList[thumb_Coord[1]][0]:
                # #         rUpCount += 1
                # # 0 = -3, 1 = -1, 2 = 1, 3 = 3, 4 = 5
                # rUpCount = int(int(rUpCount - 1)/int(2)) + 2
                # lUpCount = int(int(lUpCount - 1)/int(2)) + 2
                # print("R ct: " + str(rUpCount))
                # print("L ct: " + str(lUpCount))

                # Process whether a new input should be activated
                # On the left side
                if lUpCount == lUpCountInit:  # If there hasn't been a change in the left-hand count since last loop
                    lHandDoesShow = False
                elif lHandLoopsBetween < 6:  # If the last time a new input was activated was less than 6 loops ago
                    lHandDoesShow = False
                else:
                    lHandDoesShow = True

                # On the right side
                if rUpCount == rUpCountInit:
                    rHandDoesShow = False
                elif rHandLoopsBetween < 6:
                    rHandDoesShow = False
                else:
                    rHandDoesShow = True

                # If there is a new hand, wait 15 loops before processing hand gestures
                if firstHandInstance:
                    timeOnScreen = 0

                if timeOnScreen > 15:

                    # Process the number of fingers on the screen
                    # Right hand
                    if rUpCount == 1 and rHandDoesShow:  # If the right hand has one finger up and a new input can be activated
                        keyboard.press('l')  # Press the A button
                        print("A")
                        rHandLoopsBetween = 0
                    elif (rUpCount != rUpCountInit) and (rUpCount != 1 and rHandLoopsBetween >= 1):
                        keyboard.release('l')  # Otherwise, unpress the A button
                    if rUpCount == 2 and rHandDoesShow:  # If the right hand has two fingers up and a new input can be activated
                        keyboard.press(Key.enter)  # Press the Start button
                        print("Start")
                        rHandLoopsBetween = 0
                    elif (rUpCount != rUpCountInit) and (rUpCount != 2 and rHandLoopsBetween >= 1):
                        keyboard.release(Key.enter)  # Otherwise, unpress the Start button
                    if rUpCount == 3 and rHandDoesShow:  # If the right hand has three fingers up and a new input can be activated
                        keyboard.press('o')  # Press the Right Bumper
                        print("Right Bumper")
                        rHandLoopsBetween = 0
                    elif (rUpCount != rUpCountInit) and (rUpCount != 3 and rHandLoopsBetween >= 1):
                        keyboard.release('o')  # Otherwise, unpress the Right Bumper

                    # Left hand
                    if lUpCount == 1 and lHandDoesShow:
                        keyboard.press('k')  # Press the B button
                        print("B")
                        lHandLoopsBetween = 0
                    elif (lUpCount != lUpCountInit) and (lUpCount != 1 and lHandLoopsBetween >= 1):
                        keyboard.release('k')  # Otherwise, unpress the B button
                    if lUpCount == 2 and lHandDoesShow:
                        keyboard.press(Key.backspace)  # Press the Select button
                        print("Select")
                        lHandLoopsBetween = 0
                    elif (lUpCount != lUpCountInit) and (lUpCount != 2 and lHandLoopsBetween >= 1):
                        keyboard.release(Key.backspace)  # Otherwise, unpress the Select button
                    elif lUpCount == 3 and lHandDoesShow:
                        keyboard.press('i')  # Press the Left Bumper
                        print("Left Bumper")
                        lHandLoopsBetween = 0
                    elif (lUpCount != lUpCountInit) and (lUpCount != 3 and lHandLoopsBetween >= 1):
                        keyboard.release('i')  # Otherwise, unpress the left bumper

                # Update how many loops a hand has been on screen
                timeOnScreen += 1

                # Update upCountInit with last loops value to compare if there has been a change
                if handType == 1 and rHandLoopsBetween >= 5:
                    rUpCountInit = rUpCount
                if handType == 2 and rHandLoopsBetween >= 5:
                    lUpCountInit = lUpCount

                # Update how many loops have taken place since the last gesture
                if rHandLoopsBetween < 6 and handType == 1:
                    rHandLoopsBetween += 1
                if lHandLoopsBetween < 6 and handType == 2:
                    lHandLoopsBetween += 1

            # Take old value of hands on screen to compare against next loop
            newHandCheck = len(handLandmarks)
        else:
            # There are no hands on screen
            newHandCheck = 0

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break

        time += 1
cap.release()
