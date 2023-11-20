import cv2
import mediapipe as mp
import urllib.request
import numpy as np


URL = "https://img.hollisterco.com/is/image/anf/KIC_324-3191-0005-600_prod1.jpg?policy=product-extra-large"

def get_image():
    image_url = URL
    response = urllib.request.urlopen(image_url)
    img_array = np.array(bytearray(response.read()), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return img

def draw(img):
    mp_face_detection = mp.solutions.face_detection
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                continue
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            h, w, _ = image.shape
            overlay_img = img

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    y, x = int((bboxC.ymin) * h), int(bboxC.xmin * w)
                    y, x, width, height = int((bboxC.ymin) * h), int(bboxC.xmin * w), int(bboxC.width * w), \
                        int(bboxC.height * h)

                    new_w = 3 * width
                    scale = new_w / overlay_img.shape[1]
                    overlay_img = cv2.resize(overlay_img,
                                             (int(overlay_img.shape[0] * scale), int(overlay_img.shape[1] * scale)))
                    oh,ow, _ = overlay_img.shape
                    try:
                        min_x = x+width//2-(ow//2)
                        min_y = int(y + height * 0.8)
                        max_x = min_x + ow
                        max_y = min_y + oh
                        if max_y>h:
                            max_y = h
                        if max_x>w:
                            max_x = w
                        for i in range(min_y, max_y):
                            for j in range(min_x, max_x):
                                p = overlay_img[i - min_y, j - min_x]
                                if p[0] > 200 and p[1] > 200 and p[2] > 200:
                                    continue
                                image[i, j] = p
                    except:
                        continue
                    # mp_drawing.draw_detection(image, detection)

            cv2.imshow('Fashion App', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()

if __name__ == '__main__':
    image = get_image()
    draw(image)

