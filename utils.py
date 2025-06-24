import pyautogui
import cv2
import math

def mark_index_finger(hand_landmarks, w, h, image):
    index_finger_indices = [5, 6, 7, 8]

    for i in index_finger_indices:
        lm = hand_landmarks.landmark[i]
        cx, cy = int((1 - lm.x) * w), int(lm.y * h)
        cv2.circle(image, (cx, cy), 8, (0, 255, 0), -1)


def get_angle(base, tip):
    angle = math.atan((tip[1] - base[1]) / (tip[0] - base[0])) * 180 / math.pi
    if angle < 0:
        angle += 180

    return angle


def draw_angle(angle, base, w, h, image):
    cx, cy = int(base[0] * w), int(base[1] * h)
    cv2.ellipse(image, (cx, cy), (30, 30), 180, 0, angle, (0, 0, 255), 3)
    cv2.line(image, (cx, cy), (cx - 50, cy), (0, 0, 255), 3)

    angle_text = f"{angle:.1f}"
    cv2.putText(image, angle_text, (cx - 20, cy - 10),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7, color=(255, 255, 255), thickness=2)


def get_new_coord(length, angle, axis):
    new_x = length * math.cos(angle * math.pi / 180)
    new_y = math.sqrt(length ** 2 - new_x ** 2)

    return axis[0] - new_x, axis[1] - new_y


def draw_lines_connecting_nodes(hand_landmarks, w, h, image):
    for i in range(5, 8):
        x1, y1 = int((1 - hand_landmarks.landmark[i].x) * w), int(hand_landmarks.landmark[i].y * h)
        x2, y2 = int((1 - hand_landmarks.landmark[i + 1].x) * w), int(hand_landmarks.landmark[i + 1].y * h)
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)


def draw_fire_text(was_opened, closed, cx, cy, image):
    if not was_opened:
        cv2.putText(image, "Fired", (cx - 10, cy),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.7, color=(255, 255, 255), thickness=2)
    else:
        cv2.putText(image, "Wait" if not closed else "Fire", (cx - 10, cy),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.7, color=(255, 255, 255), thickness=2)


def handle_left_hand(hand_landmarks, w, h, image, axis):
    # marking index finger
    mark_index_finger(hand_landmarks, w, h, image)

    # determine angle
    base = (1 - hand_landmarks.landmark[5].x, hand_landmarks.landmark[5].y)
    tip = (1 - hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)
    angle = get_angle(base, tip)

    if tip[1] > base[1]:
        print("Invalid")
    else:
        # Drawing angle
        draw_angle(angle, base, w, h, image)

        # Move mouse
        length = 120
        new_x, new_y = get_new_coord(length, angle, axis)
        pyautogui.moveTo(new_x, new_y)

    # draw lines connecting nodes
    draw_lines_connecting_nodes(hand_landmarks, w, h, image)


def is_hand_closed(hand_landmarks):
    closed = True

    # Logic to decide if hand is open or closed
    for tip, base in ((8, 6), (12, 10), (16, 14), (20, 18)):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[base].y:
            closed = False
            break

    return closed


def handle_right_hand(hand_landmarks, was_opened, w, h, image):
    cx, cy = int((1 - hand_landmarks.landmark[9].x) * w), int(hand_landmarks.landmark[9].y * h)
    closed = is_hand_closed(hand_landmarks)

    if not closed:
        was_opened = True

    # Decide if hand was reset after closing once preventing continuous fire
    draw_fire_text(was_opened, closed, cx, cy, image)

    # Firing
    if closed:
        pyautogui.click() if was_opened else None
        was_opened = False

    return was_opened
