import cv2
import mediapipe as mp
import random
import time

# ---------------- CAMERA ----------------
cap = cv2.VideoCapture(1)

# ---------------- MEDIAPIPE ----------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)

# ---------------- GAME VARIABLES ----------------
startGame = False
stateResult = False
initialTime = 0
scores = [0, 0]
aiMove = None
resultText = ""
resultColor = (255, 255, 255)

# ---------------- FINGER COUNT FUNCTION ----------------
def countFingers(handLandmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    if handLandmarks.landmark[tips[0]].x < handLandmarks.landmark[tips[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    for i in range(1, 5):
        if handLandmarks.landmark[tips[i]].y < handLandmarks.landmark[tips[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


while True:
    imgBG = cv2.imread("Resources/BG.png")
    if imgBG is None:
        print("BG.png not found!")
        break

    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    playerMove = None

    # ---------------- HAND DETECTION ----------------
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            fingers = countFingers(handLms)

            if fingers == [0, 0, 0, 0, 0]:
                playerMove = 1
            elif fingers == [1, 1, 1, 1, 1]:
                playerMove = 2
            elif fingers == [0, 1, 1, 0, 0]:
                playerMove = 3

    # ---------------- GAME LOGIC ----------------
    if startGame:
        if not stateResult:
            timer = time.time() - initialTime

            cv2.putText(imgBG, str(int(timer)),
                        (630, 450),
                        cv2.FONT_HERSHEY_PLAIN, 6,
                        (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                aiMove = random.randint(1, 3)

                if playerMove is None:
                    resultText = "NO MOVE!"
                    resultColor = (255, 255, 255)
                else:
                    if (playerMove == 1 and aiMove == 3) or \
                       (playerMove == 2 and aiMove == 1) or \
                       (playerMove == 3 and aiMove == 2):
                        scores[1] += 1
                        resultText = "YOU WIN!"
                        resultColor = (0, 255, 0)

                    elif (playerMove == 3 and aiMove == 1) or \
                         (playerMove == 1 and aiMove == 2) or \
                         (playerMove == 2 and aiMove == 3):
                        scores[0] += 1
                        resultText = "AI WINS!"
                        resultColor = (0, 0, 255)

                    else:
                        resultText = "DRAW!"
                        resultColor = (0, 255, 255)

    # ---------------- PERFECT CAMERA BOX ----------------
    # Exact coordinates matching your purple player box
    cam_x1 = 880
    cam_y1 = 310
    cam_x2 = 1240
    cam_y2 = 670

    cam_w = cam_x2 - cam_x1
    cam_h = cam_y2 - cam_y1

    imgScaled = cv2.resize(img, (cam_w, cam_h))
    imgBG[cam_y1:cam_y2, cam_x1:cam_x2] = imgScaled

    # ---------------- AI IMAGE ----------------
    if stateResult and aiMove is not None:
        imgAI = cv2.imread(f"Resources/{aiMove}.png")
        if imgAI is not None:
            imgBG[330:330+imgAI.shape[0],
                  180:180+imgAI.shape[1]] = imgAI

    # ---------------- FIXED SCORES ----------------
    # AI score
    cv2.putText(imgBG, str(scores[0]),
                (540, 215),
                cv2.FONT_HERSHEY_PLAIN, 4,
                (255, 255, 255), 6)

    # Player score
    cv2.putText(imgBG, str(scores[1]),
                (1085, 215),
                cv2.FONT_HERSHEY_PLAIN, 4,
                (255, 255, 255), 6)

    # ---------------- RESULT TEXT (Centered + Lowered) ----------------
    if resultText != "":
        (text_w, text_h), _ = cv2.getTextSize(
            resultText,
            cv2.FONT_HERSHEY_SIMPLEX,
            2.5, 5
        )

        text_x = (imgBG.shape[1] - text_w) // 2
        text_y = 160   # lowered slightly

        cv2.putText(imgBG, resultText,
                    (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2.5,
                    resultColor,
                    5)

    cv2.imshow("Rock Paper Scissors AI", imgBG)

    key = cv2.waitKey(1)

    if key == ord('s'):
        startGame = True
        stateResult = False
        initialTime = time.time()
        resultText = ""

    if key == ord('r'):
        scores = [0, 0]
        startGame = False
        stateResult = False
        resultText = ""

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()