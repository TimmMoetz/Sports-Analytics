from operator import indexOf
import cv2
import mediapipe as mp
import time
import tkinter as tk
from tkinter import N, filedialog
import csv
import pandas as pd

# select video-file with file-dialog:
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()
if file_path==():
    exit()

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils
pTime = 0

cap = cv2.VideoCapture(file_path)

columns = ["27x", "27y", "27z", "28x", "28y", "28z", "29x", "29y", "29z", 
    "30x", "30y", "30z", "31x", "31y", "31z", "32x", "32y", "32z"]
df = pd.read_csv('Runner1-Joggen-incomplete.csv', index_col=0)
print(df)
print(len(df.index))
frame_count = 0
# iterate through frames of video
while True:
    print(frame_count)
    success, img = cap.read()   # img is one frame/image
    if not success:
        print("completed")
        df = df.dropna()
        break
    if frame_count >= len(df.index):
        print("completed with cut")
        print(len(df.index))
        break
    key = cv2.waitKey(1)   # cancel with ESC key
    if key == 27:
        print("canceled")
        break

    # draw pose-landmarks
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    if results.pose_landmarks:
        #mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

        row = df.loc[frame_count].values.flatten().tolist()
        # print id and coordinates of landmarks
        for id, landmark in enumerate(results.pose_landmarks.landmark):
            # see Blaze Pose Keypoint Topology for meaning of id, e.g. id=32 is "left foot index"
            relevant_ids = [27,28,29,30,31,32]
            if id in relevant_ids:
                print("ID: ", id)
                print("X: ", landmark.x)
                print("Y: ", landmark.y)
                print("Z: ", landmark.z) 
                print()

                row[columns.index(str(id)+'z')] = landmark.x
                if id == 31 or id == 32:
                    row[columns.index(str(id)+'y')] = landmark.y
                else:
                    y_of_perspective_hinten = df.loc[frame_count][str(id)+"y"]
                    mean = (float(y_of_perspective_hinten) + landmark.y) / 2
                    row[columns.index(str(id)+'y')] = mean
                    print(y_of_perspective_hinten)
                    print(landmark.y)
                    print(mean)

        df.loc[frame_count] = row

    """ # display fps
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)

    # display frame/image
    cv2.rectangle(img, (0, 0), (1200, 1200), (0, 0, 0), -1)
    #resized_img = cv2.resize(img, (675, 1200))   
    resized_img = cv2.resize(img, (475, 900))   
    cv2.imshow("Image", resized_img) """

    frame_count+=1
            
print(df)
df.to_csv('Runner1-Joggen.csv')