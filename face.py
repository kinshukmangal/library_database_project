import cv2
from deepface import DeepFace
import os

def capture_face_image(output_path="captured_face.jpg"):
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("📷 Face Login")

    print("Look at the camera. Press SPACE to capture.")
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to capture frame.")
            break
        cv2.imshow("📷 Face Login", frame)
        k = cv2.waitKey(1)
        if k % 256 == 32:  # SPACE pressed
            cv2.imwrite(output_path, frame)
            print(f"✅ Face captured and saved to {output_path}")
            break

    cam.release()
    cv2.destroyAllWindows()
    return output_path

def match_face_to_user(captured_path, known_faces_dir="library_app/known_faces"):
    for filename in os.listdir(known_faces_dir):
        if filename.endswith(".jpg"):
            known_path = os.path.join(known_faces_dir, filename)
            try:
                result = DeepFace.verify(captured_path, known_path, enforce_detection=False)
                if result["verified"]:
                    print(f"✅ Match found: {filename}")
                    name_part = filename.replace(".jpg", "")
                    first, last = name_part.split("_")
                    return first.capitalize(), last.capitalize()
            except Exception as e:
                print(f"❌ Error comparing with {filename}: {e}")
    return None, None
