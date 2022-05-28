import cv2
import mediapipe as mp
import time
import pandas as pd
import os

dir = "../../daten/hinten"

def write_keypoints(filepath, filename):
    mpPose = mp.solutions.pose
    pose = mpPose.Pose()
    mpDraw = mp.solutions.drawing_utils
    pTime = 0

    cap = cv2.VideoCapture(filepath)

    columns = ["23x", "23y", "23z", "24x", "24y", "24z", "25x", "25y", "25z", 
        "26x", "26y", "26z","27x", "27y", "27z", "28x", "28y", "28z", "29x", "29y", "29z", 
        "30x", "30y", "30z", "31x", "31y", "31z", "32x", "32y", "32z"]
    data = []

    # iterate through frames of video
    while True:
        print(len(data))
        success, img = cap.read()   # img is one frame/image
        if not success:
            break

        # draw pose-landmarks
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)

        cv2.rectangle(img, (0, 0), (1200, 1200), (0, 0, 0), -1)   # anonymization

        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)

            row = ['' for i in range(len(columns))] 
            # print id and coordinates of landmarks
            for id, landmark in enumerate(results.pose_landmarks.landmark):
                # see Blaze Pose Keypoint Topology for meaning of id, e.g. id=32 is "left foot index"
                relevant_ids = [23,24,25,26,27,28,29,30,31,32]
                if id in relevant_ids:
                    print("ID: ", id)
                    print("X: ", landmark.x)
                    print("Y: ", landmark.y)
                    print("Z: ", landmark.z) 
                    print()

                    row[columns.index(str(id)+'x')] = landmark.x

                    if id != 31 and id != 32:
                        row[columns.index(str(id)+'y')] = landmark.y
                
            data.append(row)

            # display fps
            cTime = time.time()
            fps = 1/(cTime-pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0), 3)

            # display frame/image
            #resized_img = cv2.resize(img, (675, 1200))   
            resized_img = cv2.resize(img, (475, 900))   
            cv2.imshow("Image", resized_img)
            cv2.waitKey(1) 

    df = pd.DataFrame(data, index=range(len(data)), columns=[columns])
    print(df)   
    df.to_csv("incomplete-" + str(filename[:-4])+ ".csv")

a_directory = dir
for filename in os.listdir(a_directory):
    filepath = os.path.join(a_directory, filename)
    print(filename)
    write_keypoints(filepath, filename)