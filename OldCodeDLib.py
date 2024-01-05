import cv2
import dlib
import math
from pynput.keyboard import Key, Controller
import mediapipe

# define keyboard
keyboard = Controller()

# Load the detector
detector = dlib.get_frontal_face_detector()
mp_Hands = mediapipe.solutions.hands
hands = mp_Hands.Hands()
mpDraw = mediapipe.solutions.drawing_utils
finger_Coord = [(8, 6), (12, 10), (16, 14), (20, 18)]
thumb_Coord = (4,2)

# Load the predictor
predictor = dlib.shape_predictor("shape_predictor_81_face_landmarks.dat")

# read the image
cap = cv2.VideoCapture(0)

doesShow = False
controllerOutputInit = -3
loopsBetween = 0
moveCombo = []
moveComboTime = []
moveComboTimeTotal = 0
controllerOutput = None

handType = 0
handLoopsBetween = 0
handDoesShow = False
upCountInit = -1
handTypeInit = -1

while True:
    _, frame = cap.read()
    # Convert image into grayscale
    gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

    # Convert image into RGB
    RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Use detector to find landmarks
    faces = detector(gray)

    # Use hands to find landmarks
    results = hands.process(RGB)
    handLandmarks = results.multi_hand_landmarks

    if handLandmarks:
        handList = []
        for hand in handLandmarks:
            mpDraw.draw_landmarks(frame, hand, mp_Hands.HAND_CONNECTIONS)
            for idx, lm in enumerate(hand.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                handList.append((cx, cy))
                for point in handList:
                    cv2.circle(img=frame, center=point, radius=3, color=(0, 255, 0), thickness=-1)

            # handType is 1 if left and 2 if right hand
            if handList[8][0] < handList[17][0]:
                handType = 1
            elif handList[8][0] > handList[17][0]:
                handType = 2

            upCount = 0
            for coordinate in finger_Coord:
                if handList[coordinate[0]][1] < handList[coordinate[1]][1]:
                    upCount += 1
            if handType == 1:
                if handList[thumb_Coord[0]][0] < handList[thumb_Coord[1]][0]:
                    upCount += 1
            elif handType == 2:
                if handList[thumb_Coord[0]][0] > handList[thumb_Coord[1]][0]:
                    upCount += 1

            #print(handLoopsBetween)
            if upCount == upCountInit and handType == handTypeInit:
                handDoesShow = False
            elif handLoopsBetween < 9:
                handDoesShow = False
            else:
                handDoesShow = True

            #rint(handType)
            #print(upCount)

            if (handType == 2 and upCount == 1) and handDoesShow:
                keyboard.press('l')
                print("A")
                handLoopsBetween = 0
            elif (handType == 1 and upCount == 1) and handDoesShow:
                keyboard.press('k')
                print("B")
                handLoopsBetween = 0
            elif (handType == 2 and upCount == 2) and handDoesShow:
                keyboard.press(Key.enter)
                print("Start")
                handLoopsBetween = 0
            elif (handType == 1 and upCount == 2) and handDoesShow:
                keyboard.press(Key.backspace)
                print("Select")
                handLoopsBetween = 0
            elif (handType == 2 and upCount == 3) and handDoesShow:
                keyboard.press('o')
                print("Right Bumper")
                handLoopsBetween = 0
            elif (handType == 1 and upCount == 3) and handDoesShow:
                keyboard.press('i')
                print("Left Bumper")
                handLoopsBetween = 0
            else:
                keyboard.release('l')
                keyboard.release('k')
                keyboard.release(Key.enter)
                keyboard.release(Key.backspace)
                keyboard.release('o')
                keyboard.release('i')
                #handLoopsBetween = 0
            upCountInit = upCount
            handTypeInit = handType
        handLoopsBetween += 1




    for face in faces:
        x1 = face.left()  # left point
        y1 = face.top()  # top point
        x2 = face.right()  # right point
        y2 = face.bottom()  # bottom point

        faceArea = ((x2 - x1) * (y2 - y1))

        # Create landmark object
        landmarks = predictor(image=gray, box=face)

        # Loop through all the points
        for n in range(0, 81):
            x = landmarks.part(n).x
            y = landmarks.part(n).y

            # Draw a circle
            cv2.circle(img=frame, center=(x, y), radius=3, color=(0, 255, 0), thickness=-1)

        # 27 (nose) 71 (Forehead)
        topNose = landmarks.part(27)
        middleForehead = landmarks.part(71)

        # 74, 75 (far left and right forehead) 17, 26 (far left and right eyebrow)
        leftForehead = landmarks.part(75)
        rightForehead = landmarks.part(74)

        # 25, 45 (left eyebrow and eye), 18, 36 (right eyebrow and eye)
        leftEyebrow = landmarks.part(25)
        rightEyebrow = landmarks.part(18)
        leftEye = landmarks.part(45)
        rightEye = landmarks.part(36)

        # 22, 42 (inner left eyebrow and eye) 21, 39 (inner right eyebrow and eye)
        inLeftEyebrow = landmarks.part(22)
        inRightEyebrow = landmarks.part(21)
        inLeftEye = landmarks.part(42)
        inRightEye = landmarks.part(39)

        # 1, 15 (right and left cheekbones)
        rightCheek = landmarks.part(1)
        leftCheek = landmarks.part(15)


        dBetweenNoseFore = math.sqrt(((topNose.y - middleForehead.y)**2)+(topNose.x - middleForehead.x))
        dForehead = math.sqrt(((rightForehead.x - leftForehead.x)**2)+((rightForehead.y - leftForehead.y)**2))
        dInLeftBrow = math.sqrt(((inLeftEye.y - inLeftEyebrow.y)**2)+((inLeftEye.x - inLeftEyebrow.x)**2))
        dInRightBrow = math.sqrt(((inRightEye.y - inRightEyebrow.y)**2)+((inRightEye.x - inRightEyebrow.x)**2))
        dLeftBrow = math.sqrt(((leftEye.y - leftEyebrow.y)**2)+((leftEye.x - leftEyebrow.x)**2))
        dRightBrow = math.sqrt(((rightEye.y - rightEyebrow.y)**2)+((rightEye.x - rightEyebrow.x)**2))

        dBrowAlt = leftEyebrow.y - rightEyebrow.y
        # dBrowAlt = math.sqrt(((leftEyebrow.y - rightEyebrow.y)**2)+((leftEyebrow.x - rightEyebrow.x)**2))

        #cheekSlope = (rightCheek.y - leftCheek.y) / (rightCheek.x - leftCheek.x)
        #foreSlope = (rightForehead.y - leftForehead.y) / (rightForehead.x - leftForehead.x)
        #browSlope = (leftEyebrow.y - rightEyebrow.y) / (leftEyebrow.x - rightEyebrow.x)
        #if cheekSlope != 0:
        #    foreBrowSlopeDiff = browSlope/cheekSlope
        #    print(foreBrowSlopeDiff)

        # default between 41 and 44
        # up is around 48
        # down is around 38
        eyebrowLongChecker = ((dBetweenNoseFore / dForehead) * 100)
        #print(eyebrowLongChecker)

        # 1285 is up
        lEyebrowChecker = ((dLeftBrow / dInLeftBrow) * 1000)

        # 1460 is up
        rEyebrowChecker = ((dRightBrow / dInRightBrow) * 1000)
        #print(rEyebrowChecker)

        # 25 is right, -25 is left
        browAltChecker = (dBrowAlt / dForehead) * 1000
        #print(browAltChecker)

        # 0 is neutral, 1 is up, 2 is down, 3 is right, 4 is left
        if 47 < eyebrowLongChecker < 51:
            controllerOutput = 1
        elif 37 < eyebrowLongChecker < 39.5:
            controllerOutput = 2
        elif browAltChecker > 40:
            controllerOutput = 3
        elif browAltChecker < -20:
            controllerOutput = 4
        else:
            controllerOutput = 0
        # print(eyebrowLongChecker)

    if controllerOutput == controllerOutputInit:
        doesShow = False
    elif controllerOutput == 0 and loopsBetween >= 1:
        doesShow = True
    elif loopsBetween < 7:
        doesShow = False
    else:
        doesShow = True

    if controllerOutput == 1 and doesShow == True:
        print("up")
        keyboard.press('w')
        #print("Loops between last expression: " + str(loopsBetween))
        moveCombo.append(1)
        moveComboTime.append(loopsBetween)
        loopsBetween = 0
    elif controllerOutput == 2 and doesShow == True:
        print("down")
        keyboard.press('s')
        #print("Loops between last expression: " + str(loopsBetween))
        loopsBetween = 0
    elif controllerOutput == 3 and doesShow == True:
        print("right")
        keyboard.press('d')
        loopsBetween = 0
    elif controllerOutput == 4 and doesShow == True:
        print("left")
        keyboard.press('a')
        loopsBetween = 0
    elif controllerOutput == 0 and doesShow == True:
        print("neutral")
        keyboard.release('w')
        keyboard.release('s')
        keyboard.release('d')
        keyboard.release('a')
        #print("Loops between last expression: " + str(loopsBetween))
        moveCombo.append(0)
        moveComboTime.append(loopsBetween)
        moveComboTimeTotal = sum(moveComboTime)
        #print(str(moveComboTimeTotal))
        #print(str(moveComboTime))
        loopsBetween = 0
        #print(str(moveCombo))
    loopsBetween += 1
    controllerOutputInit = controllerOutput

    # moveComboTimeTotal = sum(moveComboTime)
    doubleEyebrowMoveCombo = [1, 1, 0]
   # if moveCombo == doubleEyebrowMoveCombo and moveComboTimeTotal <= 80:
        #print()
        #print("Double eyebrow lift")
        #break

    if len(moveCombo) >= 3:
        moveCombo.pop(0)
        moveComboTime.pop(0)
        if moveComboTimeTotal > 80:
            moveComboTimeTotal = 0

    # show the image
    cv2.imshow(winname="Face", mat=frame)

    # Exit when escape is pressed
    if cv2.waitKey(delay=1) == 27:
        break

# When everything done, release the video capture and video write objects
cap.release()

# Close all windows
cv2.destroyAllWindows()
