# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the
# license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

import cv2 as cv
import numpy as np
from time import time

HUMAN_ID = 0


class YOLOv3Detector:
  def __init__(self, conf_thresh=0.5, nms_thresh=0.4, in_width=416, in_height=416):
    # Initialize the parameters
    self.conf_thresh = conf_thresh
    self.nms_thresh = nms_thresh
    self.in_width = in_width
    self.in_height = in_height

    # Load names of self.classes
    self.classes = None
    with open("vision/detection/coco.names", 'rt') as f:
      self.classes = f.read().rstrip('\n').split('\n')

    # Give the configuration and weight files for the model and load the network using them.
    self.net = cv.dnn.readNetFromDarknet("vision/detection/yolov3-tiny.cfg",
                                         "vision/detection/yolov3-tiny.weights")
    self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    layer_names = self.net.getLayerNames()
    self.output_names = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

  # Remove the bounding boxes with low confidence using non-maxima suppression
  def postprocess(self, frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    # Scan through all the bounding boxes output from the self.network and keep only the ones with
    # high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
      for detection in out:
        scores = detection[5:]
        classId = np.argmax(scores)
        confidence = scores[classId]
        if confidence > self.conf_thresh and classId == HUMAN_ID:  # Only detect humans
          center_x = int(detection[0] * frameWidth)
          center_y = int(detection[1] * frameHeight)
          width = int(detection[2] * frameWidth)
          height = int(detection[3] * frameHeight)
          left = int(center_x - width / 2)
          top = int(center_y - height / 2)
          classIds.append(classId)
          confidences.append(float(confidence))
          boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, self.conf_thresh, self.nms_thresh)
    nms_boxes = [boxes[i[0]] for i in indices]

    return nms_boxes

  def detect_img(self, img):
    # Create a 4D blob from a frame.
    all_start = time()
    blob = cv.dnn.blobFromImage(img, 1 / 255, (self.in_width, self.in_height), [0, 0, 0], 1, crop=False)
    blob_time = time() - all_start

    # Sets the input to the self.network
    self.net.setInput(blob)

    # Runs the forward pass to get output of the output layers
    preds_start = time()
    preds_raw = self.net.forward(self.output_names)
    pred_time = time() - preds_start

    # Remove the bounding boxes with low confidence
    post_start = time()
    preds = self.postprocess(img, preds_raw)
    post_time = time() - post_start

    # Put efficiency information. The function getPerfProfile returns the overall time for
    # inference(t) and the timings for each of the layers(in layersTimes)
    all_time = time() - all_start
    all_fps = 1 / all_time
    label = 'Inference time: %.2f ms | %.2f fps' % (all_time / 1000, all_fps)
    cv.putText(img, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    # print(label)

    # print('-'*30)
    # print('All  fps :', all_fps)
    # print('All  time:', all_time)
    # print('Blob time:', blob_time)
    # print('Pred time:', pred_time)
    # print('Post time:', post_time)

    out_img = img.astype(np.uint8)

    return preds, out_img
