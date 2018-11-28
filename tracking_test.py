'''
    File name         : object_tracking.py
    File Description  : Multi Object Tracker Using Kalman Filter
                        and Hungarian Algorithm
    Author            : Srini Ananthakrishnan
    Date created      : 07/14/2017
    Date last modified: 07/16/2017
    Python Version    : 2.7
'''

# Import python libraries
import cv2
import copy
from vision.tracking.tracker import Tracker
from vision.detection.yolov3_detector import YOLOv3Detector


def draw_tracks(frame, tracker):
  track_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (0, 255, 255), (255, 0, 255), (255, 127, 255),
                  (127, 0, 255), (127, 0, 127)]

  for track in tracker.tracks:
    color = track_colors[track.track_id % len(track_colors)]
    print(color)
    draw_trace(frame, track, color)
    draw_boxes(frame, track, color)


def draw_trace(frame, track, color):
  # For identified object tracks draw tracking line
  # Use various colors to indicate different track_id
  for j in range(len(track.trace) - 1):
    # Draw trace line
    x1 = track.trace[j][0][0]
    y1 = track.trace[j][1][0]
    x2 = track.trace[j + 1][0][0]
    y2 = track.trace[j + 1][1][0]
    cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)


# Draw the predicted bounding box
def draw_boxes(frame, track, color):
  box = track.box
  left, top, width, height = box
  right = left + width
  bottom = top + height

  # Draw a bounding box.
  cv2.rectangle(frame, (left, top), (right, bottom), color, 3)


def main():
  """Main function for multi object tracking
  Usage:
      $ python2.7 objectTracking.py
  Pre-requisite:
      - Python2.7
      - Numpy
      - SciPy
      - Opencv 3.0 for Python
  Args:
      None
  Return:
      None
  """

  # Create opencv video capture object
  cap = cv2.VideoCapture('test/tracking.mov')

  # Create Object Detector
  detector = YOLOv3Detector()

  # Create Object Tracker
  tracker = Tracker(160, 30, 5, 100)

  # Variables initialization
  pause = False

  # Infinite loop to process video frames
  while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Make copy of original frame
    orig_frame = copy.copy(frame)

    # Detect the objects in the frame
    box_preds, _ = detector.detect_img(frame)

    # If centroids are detected then track them
    if len(box_preds) > 0:
      # Track object using Kalman Filter
      tracker.Update(box_preds)

    draw_tracks(frame, tracker)

    cv2.imshow('Tracking', frame)
    cv2.imshow('Original', orig_frame)

    # Slow the FPS
    cv2.waitKey(10)

  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  # execute main
  main()
