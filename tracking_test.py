'''
    File name         : object_tracking.py
    File Description  : Multi Object Tracker Using Kalman Filter
                        and Hungarian Algorithm
    Author            : Srini Ananthakrishnan
    Date created      : 07/14/2017
    Date last modified: 07/16/2017
    Python Version    : 2.7
'''

import cv2
import numpy as np
from time import time

from vision.tracking.tracker import Tracker
from vision.detection.yolov3_detector import YOLOv3Detector


def draw_tracks(frame, tracker):
  track_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                  (0, 255, 255), (255, 0, 255), (255, 127, 255),
                  (127, 0, 255), (127, 0, 127)]

  for track in tracker.tracks:
    color = track_colors[track.track_id % len(track_colors)]
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
  # Create opencv video capture object
  cap = cv2.VideoCapture('test/tracking.mov')

  detector = YOLOv3Detector()
  tracker = Tracker(160, 30, 5, 100)

  vid_writer = cv2.VideoWriter(
    'test/tracking-processed.avi',
    cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
    30,
    (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

  while True:
    all_start = time()
    # Capture frame-by-frame
    ret, frame = cap.read()
    cap_time = time() - all_start

    det_start = time()
    box_preds, _ = detector.detect_img(frame)
    det_time = time() - det_start
    track_start = time()
    tracker.Update(box_preds)
    track_time = time() - track_start

    misc_start = time()
    draw_tracks(frame, tracker)
    # cv2.imshow('Tracking', frame)

    # Slow the FPS
    cv2.waitKey(10)

    vid_writer.write(frame.astype(np.uint8))
    misc_time = time() - misc_start
    all_time = time() - all_start

    print('-'*30)
    print('All fps :', 1 / all_time)
    print('All time:', all_time)
    print('Cap time:', cap_time)
    print('Det time:', det_time)
    print('Trk time:', track_time)
    print('Msc time:', misc_time)


  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()
