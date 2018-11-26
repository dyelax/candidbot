# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the
# license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

import cv2 as cv
import argparse
import sys
import numpy as np
import os.path


class YOLOv3Detector:
  def __init__(self, conf_thresh=0.5, nms_thresh=0.4, in_width=416, in_height=416):
    # Initialize the parameters
    self.conf_thresh = conf_thresh
    self.nms_thresh = nms_thresh
    self.in_width = in_width
    self.in_height = in_height

    # Load names of self.classes
    self.classes = None
    with open("coco.names", 'rt') as f:
      self.classes = f.read().rstrip('\n').split('\n')

    # Give the configuration and weight files for the model and load the network using them.
    self.net = cv.dnn.readNetFromDarknet("yolov3-tiny.cfg", "yolov3-tiny.weights")
    self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
    self.net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

    layer_names = self.net.getLayerNames()
    self.output_names = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

  # Draw the predicted bounding box
  def draw_preds(self, frame, classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (255, 178, 50), 3)

    label = '%.2f' % conf

    # Get the label for the class name and its confidence
    if self.classes:
      assert (classId < len(self.classes))
      label = '%s:%s' % (self.classes[classId], label)

    # Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.rectangle(frame, (left, top - round(1.5 * labelSize[1])),
                 (left + round(1.5 * labelSize[0]), top + baseLine), (255, 255, 255), cv.FILLED)
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 1)


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
        if confidence > self.conf_thresh:
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
    for i in indices:
      i = i[0]
      box = boxes[i]
      left = box[0]
      top = box[1]
      width = box[2]
      height = box[3]
      self.draw_preds(frame, classIds[i], confidences[i], left, top, left + width, top + height)

    return boxes

  def detect_img(self, img):
    # Create a 4D blob from a frame.
    blob = cv.dnn.blobFromImage(img, 1 / 255, (self.in_width, self.in_height), [0, 0, 0], 1, crop=False)

    # Sets the input to the self.network
    self.net.setInput(blob)

    # Runs the forward pass to get output of the output layers
    preds_raw = self.net.forward(self.output_names)

    # Remove the bounding boxes with low confidence
    preds = self.postprocess(img, preds_raw)

    # Put efficiency information. The function getPerfProfile returns the overall time for
    # inference(t) and the timings for each of the layers(in layersTimes)
    t, _ = self.net.getPerfProfile()
    perf_ms = t * 1000.0 / cv.getTickFrequency()
    perf_fps = cv.getTickFrequency() / t
    label = 'Inference time: %.2f ms | %.2f fps' % (perf_ms, perf_fps)
    cv.putText(img, label, (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
    print(label)

    out_img = img.astype(np.uint8)

    return preds, out_img

  @staticmethod
  def get_centers(preds):
    centers = []
    for pred in preds:
      left, top, width, height = pred
      center_x = left + (width / 2)
      center_y = top + (height / 2)

      centers.append((center_x, center_y))

    return centers


def test():
  parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
  parser.add_argument('--image', help='Path to image file.')
  parser.add_argument('--video', help='Path to video file.')
  args = parser.parse_args()

  detector = YOLOv3Detector()

  # Process inputs
  winName = 'Deep learning object detection in OpenCV'
  cv.namedWindow(winName, cv.WINDOW_NORMAL)

  outputFile = "yolo_out_py.avi"
  if args.image:
    # Open the image file
    if not os.path.isfile(args.image):
      print("Input image file ", args.image, " doesn't exist")
      sys.exit(1)
    cap = cv.VideoCapture(args.image)
    outputFile = args.image[:-4] + '_yolo_out_py.jpg'
  elif args.video:
    # Open the video file
    if not os.path.isfile(args.video):
      print("Input video file ", args.video, " doesn't exist")
      sys.exit(1)
    cap = cv.VideoCapture(args.video)
    outputFile = args.video[:-4] + '_yolo_out_py.avi'
  else:
    # Webcam input
    cap = cv.VideoCapture(0)

  # Get the video writer initialized to save the output video
  if not args.image:
    vid_writer = cv.VideoWriter(outputFile, cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (
      round(cap.get(cv.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv.CAP_PROP_FRAME_HEIGHT))))

  while cv.waitKey(1) < 0:

    # get frame from the video
    hasFrame, frame = cap.read()

    # Stop the program if reached end of video
    if not hasFrame:
      print("Done processing !!!")
      print("Output file is stored as ", outputFile)
      cv.waitKey(3000)
      break

    _, frame = detector.detect_img(frame)

    # Write the frame with the detection boxes
    if (args.image):
      cv.imwrite(outputFile, frame.astype(np.uint8))
    else:
      vid_writer.write(frame.astype(np.uint8))

    cv.imshow(winName, frame)


def test_img(path):
  detector = YOLOv3Detector()
  img = cv.imread(path)
  out_path = path[:-4] + '-processed.jpg'

  preds, out_img = detector.detect_img(img)

  print(preds)
  print(detector.get_centers(preds))
  cv.imwrite(out_path, out_img)

if __name__ == '__main__':
  for _ in range(10):
    test_img('../test/0.jpg')
    # test_img('../test/1.jpg')
    # test_img('../test/2.jpg')
    # test_img('../test/3.jpg')
    # test_img('../test/4.jpg')

