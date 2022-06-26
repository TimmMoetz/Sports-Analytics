
import cv2
import mediapipe as mp
import pandas as pd
import os
import math

#------------------------------------- variables ---------------------------------------
dir_hinten = "../../data/hinten"
dir_metrics = "../../data/metrics_pronation"
dir_csv = "../../data/csv"

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils


#--------------------------------------- functions --------------------------------

def display_img(img):
    # display frame/image
    #resized_img = cv2.resize(img, (675, 1200))   # big screen 
    resized_img = cv2.resize(img, (475, 900))    # small screen
    cv2.imshow("Image", resized_img)

def derive_metrics(filepath, filename):
    cap = cv2.VideoCapture(filepath)

    csv_filepath = os.path.join(dir_csv, str(filename[:-4]) + '.csv')
    df = pd.read_csv(csv_filepath, index_col=0)

    data = dict( left = [], right = [] )
    frame_count = 0
    pause_at_next_frame = False

    # iterate through frames of video
    while True:
        print("frame:", frame_count)
        success, img = cap.read()   # img is one frame/image
        if not success:    # gets triggered when all frames have been iterated
            print("completed")
            break
        
        # calculate and draw pose-landmarks
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(imgRGB)
        cv2.rectangle(img, (0, 0), (1200, 900), (0, 0, 0), -1)   # anonymization
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            display_img(img)

            if len(data["right"]) == 10 and len(data["left"]) == 10:
                break
            
            if pause_at_next_frame:
                pause_at_next_frame = pause_video(df, data, frame_count)
                print(data)
                print(len(data["left"]))
                print(len(data["right"]))

            key = cv2.waitKey(1)
            if key == ord('p'):
                pause_at_next_frame = pause_video(df, data, frame_count)
                print(data)
                print(len(data["left"]))
                print(len(data["right"]))
            if key == ord('e'):   # exit video, write csv and go to next video
                break

            frame_count+=1
                
    print(data)
    new_df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()})
    print(new_df)
    metrics_filepath = os.path.join(dir_metrics, str(filename[:-4])+ "_metrics_pronation.csv")
    new_df.to_csv(metrics_filepath)

def pause_video(df, data, frame_count):
    key = cv2.waitKey(-1) # wait until any key is pressed
    if key == ord('p'):   # pause at next frame
        return True
    if key == ord('s'):   # save frame and pause at next frame
        if len(data["left"]) < 10:
            angle = culculate_metric_left(df, frame_count)
            data["left"].append(angle)
        return True
    if key == ord('d'):   # save frame and pause at next frame
        if len(data["right"]) < 10:
            angle = culculate_metric_right(df, frame_count)
            data["right"].append(angle)
        return True
    if key == ord('q'):   # delete last entry in "left"
        data["left"].pop()
        return True
    if key == ord('w'):   # delete last entry in "right"
        data["right"].pop()
        return True
    else:                 # continue
        return False

def culculate_metric_right(df, frame):
    knee_x, knee_y = df.iloc[frame]["25z"], df.iloc[frame]["25y"]
    ankle_x, ankle_y = df.iloc[frame]["27z"], df.iloc[frame]["27y"]
    heel_x, heel_y = df.iloc[frame]["29z"], df.iloc[frame]["29y"]

    angle = getAngle((knee_x, knee_y), (ankle_x, ankle_y), (heel_x, heel_y))
    print(angle)
    return angle

def culculate_metric_left(df, frame):
    knee_x, knee_y = df.iloc[frame]["26z"], df.iloc[frame]["26y"]
    ankle_x, ankle_y = df.iloc[frame]["28z"], df.iloc[frame]["28y"]
    heel_x, heel_y = df.iloc[frame]["30z"], df.iloc[frame]["30y"]

    angle = getAngle((knee_x, knee_y), (ankle_x, ankle_y), (heel_x, heel_y))
    print(angle)
    return angle

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang
#--------------------------------- main loop ----------------------------------

# loop through all videos with perspective "hinten"
for filename in os.listdir(dir_hinten):
    filepath = os.path.join(dir_hinten, filename)
    print(filename)
    derive_metrics(filepath, filename)