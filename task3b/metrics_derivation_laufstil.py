import cv2
import mediapipe as mp
import pandas as pd
import os
import math

#------------------------------------- variables ---------------------------------------
dir_seite = "../../data/seite"
dir_csv = "../../data/csv"
dir_metrics = "../../data/metrics_laufstil"

mpPose = mp.solutions.pose
pose = mpPose.Pose()
mpDraw = mp.solutions.drawing_utils

#--------------------------------------- functions --------------------------------

def display_img(img):
    # display frame/image
    #resized_img = cv2.resize(img, (675, 1200))   # big screen 
    resized_img = cv2.resize(img, (475, 900))    # small screen
    cv2.imshow("Image", resized_img)
    cv2.waitKey(1) 

def derive_metrics(filepath, filename):
    cap = cv2.VideoCapture(filepath)

    csv_filepath = os.path.join(dir_csv, str(filename[:-4]) + '.csv')
    df = pd.read_csv(csv_filepath, index_col=0)

    # filter for the top 100 highest values of '32z' (left foot)
    canidat_df_left = df.nlargest(n=100, columns=['32z'], keep='all')
    canidat_frames_at_time_of_tread_left = canidat_df_left.index.array
    print(canidat_frames_at_time_of_tread_left)

    # filter for the top 100 highest values of '31z' (right foot)
    canidat_df_right = df.nlargest(n=100, columns=['31z'], keep='all')
    canidat_frames_at_time_of_tread_right = canidat_df_right.index.array
    print(canidat_frames_at_time_of_tread_right)

    data = dict( left = [], right = [] )
    frame_count = 0
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

            if len(data["left"]) < 10:
                if frame_count in canidat_frames_at_time_of_tread_left:
                    print("--------------")
                    angle = culculate_metric_left(df, frame_count)
                    key = cv2.waitKey(-1)  # wait until any key is pressed
                    if key == ord('s'):  # save frame
                        data["left"].append(angle)
                    if key == ord('p'):   # save previous frame
                        angle = culculate_metric_left(df, previous_canidat_frame)
                        data["left"].append(angle)
                    if key == ord('e'):   # exit video, write csv and go to next video
                        break
                    # if any other key is pressed no frame gets saved
                    previous_canidat_frame = frame_count
                    print(data)

            if len(data["right"]) < 10:
                if frame_count in canidat_frames_at_time_of_tread_right:
                    print("--------------")
                    angle = culculate_metric_right(df, frame_count)
                    key = cv2.waitKey(-1)  # wait until any key is pressed
                    if key == ord('s'):  # save frame
                        data["right"].append(angle)
                    if key == ord('p'):   # save previous frame
                        angle = culculate_metric_right(df, previous_canidat_frame)
                        data["right"].append(angle)
                    if key == ord('e'):   # exit video, write csv and go to next video
                        break
                    # if any other key is pressed no frame gets saved
                    previous_canidat_frame = frame_count
                    print(data)
            frame_count+=1
                
    print(data)
    new_df = pd.DataFrame({k:pd.Series(v) for k,v in data.items()})
    print(new_df)
    metrics_filepath = os.path.join(dir_metrics, str(filename[:-4])+ "_metrics_laufstil.csv")
    new_df.to_csv(metrics_filepath)

def culculate_metric_right(df, frame):
    foot_index_x, foot_index_y = df.iloc[frame]["31z"], df.iloc[frame]["31y"]
    heel_x, heel_y = df.iloc[frame]["29z"], df.iloc[frame]["29y"]

    angle = getAngle((foot_index_x, foot_index_y), (heel_x, heel_y), (heel_x, 0))
    print(angle)
    return angle

def culculate_metric_left(df, frame):
    foot_index_x, foot_index_y = df.iloc[frame]["32z"], df.iloc[frame]["32y"]
    heel_x, heel_y = df.iloc[frame]["30z"], df.iloc[frame]["30y"]

    angle = getAngle((foot_index_x, foot_index_y), (heel_x, heel_y), (heel_x, 0))
    print(angle)
    return angle

def getAngle(a, b, c):
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    return ang + 360 if ang < 0 else ang

#--------------------------------- main loop ----------------------------------

# loop through all videos with perspective "seite"
for filename in os.listdir(dir_seite):
    filepath = os.path.join(dir_seite, filename)
    print(filename)
    derive_metrics(filepath, filename)