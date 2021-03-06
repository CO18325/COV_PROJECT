import numpy as np
import cv2
import imutils
import os
import time
def check_distance(a,  b):

    dist = ((a[0] - b[0]) ** 2 + 550 / ((a[1] + b[1]) / 2) * (a[1] - b[1]) ** 2) ** 0.5
    calibration = (a[1] + b[1]) / 2       
    
    if 0 < dist < 0.25 * calibration:
        return True
    else:
        return False

def intial_setup():
    global net, name
    weights = "yolo/yolov4.weights"
    config = "yolo/yolov4.cfg"
    labelsPath = "yolo/coco.names"
    name = open(labelsPath).read().strip().split("\n")  
    net = cv2.dnn_DetectionModel(config, weights)
# uncomment these line while using cuda  
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    net.setInputSize(416, 416)
    net.setInputScale(1.0 / 255)
    net.setInputSwapRB(True)
    # ln = net.getLayerNames()
    # ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

def image_processing(image):

    global processedImg
    (H, W) = (None, None)
    frame = image.copy()
    if W is None or H is None:
        (H, W) = frame.shape[:2]
    # blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    # net.setInput(blob)


    confidences1 = []
    outline = []

    classes, confidences, boxes= net.detect(frame, confThreshold=0.1, nmsThreshold=0.4)
    if(not len(classes) == 0):
        for classId, confidence, box in zip(classes.flatten(), confidences.flatten(), boxes):
            if(name[classId]=="person"):
                (x, y, width, height) = box.astype("int")
                x = int(x)
                y = int(y)
                outline.append([x, y, int(width), int(height)])
                confidences1.append(float(confidence))

    box_line = cv2.dnn.NMSBoxes(outline, confidences1, 0.4, 0.5)
    
    
    
    if len(box_line) > 0:
        flat_box = box_line.flatten()
        pairs = []
        center = []
        status = [] 
        for i in flat_box:
            (x, y) = (outline[i][0], outline[i][1])
            (w, h) = (outline[i][2], outline[i][3])
            center.append([int(x + w / 2), int(y + h / 2)])
            status.append(False)

        for i in range(len(center)):
            for j in range(len(center)):
                close = check_distance(center[i], center[j])

                if close:
                    pairs.append([center[i], center[j]])
                    status[i] = True
                    status[j] = True
        index = 0

        for i in flat_box:
            (x, y) = (outline[i][0], outline[i][1])
            (w, h) = (outline[i][2], outline[i][3])
            if status[index] == True:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 150), 2)
            elif status[index] == False:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            index += 1
        for h in pairs:
            cv2.line(frame, tuple(h[0]), tuple(h[1]), (0, 0, 255), 2)
    processedImg = frame.copy()
            



def sd_gen():
    """Video streaming generator function."""
    frame_number = 0
    filename = "videos/rt3.mp4"
    intial_setup()

    cap = cv2.VideoCapture(filename)
    # cap = cv2.VideoCapture(0)
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # out = cv2.VideoWriter('videos/new.avi', fourcc, 20.0, (680,765))
    while(cap.isOpened()):
      # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            break
        timer = time.time()
        current_img = frame.copy()
        # current_img = imutils.resize(current_img, width=680)
        video = current_img.shape
        frame_number += 1
        Frame = current_img
        
        if(frame_number%3 == 0 or frame_number == 1):
            
            image_processing(current_img)
            Frame = processedImg
            print('[Info] Time Taken: {} | FPS: {}'.format(time.time() - timer, 1/(time.time() - timer)), end='\r')
        # out.write(processedImg)
        # print(processedImg.shape)
        
            
        frame = cv2.imencode('.jpg', processedImg)[1].tobytes()
        
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # time.sleep(0.1)
        key = cv2.waitKey(20)
        if key == 27:
            break