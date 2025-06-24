from utils import *
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Change according to screen the position of the shooting ball
axis = 705, 670

def main():
    cap = cv2.VideoCapture(0)
    was_opened = True

    try:
        with mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                max_num_hands=2) as hands:
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    break

                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = hands.process(image)

                # Draw the hand annotations on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image = cv2.flip(image, 1)

                h, w, _ = image.shape

                if results.multi_hand_landmarks:
                    for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):

                        if hand_info.classification[0].label == "Left":  # Angle Hand
                            # Avoid accidental wrong hand detection
                            if hand_info.classification[0].score < 0.9:
                                continue

                            handle_left_hand(hand_landmarks, w, h, image, axis)

                        else:  # Shooting hand
                            was_opened = handle_right_hand(hand_landmarks, was_opened, w, h, image)

                # Flip the image horizontally for a selfie-view display.
                cv2.imshow('MediaPipe Hands', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
