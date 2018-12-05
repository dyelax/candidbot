'''
    File name         : object_tracking.py
    File Description  : Multi Object Tracker Using Kalman Filter
                        and Hungarian Algorithm
    Author            : Srini Ananthakrishnan
    Date created      : 07/14/2017
    Date last modified: 07/16/2017
    Python Version    : 2.7
'''

from time import time

import cv2
import numpy as np

from vision.detection.yolov3.yolov3_detector import YOLOv3Detector
from vision.tracking.tracker import Tracker

from vision.visualize import draw_tracks, draw_region

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

    height = frame.shape[0]
    width = frame.shape[1]
    dist_thresh = int(height / 8)
    center_thresh = int(width / 6)

    center_x = int(width / 2)
    photo_region = ((0, height - dist_thresh), (width, height))
    center_region = ((center_x - center_thresh, 0), (center_x + center_thresh, height))

    draw_region(frame, photo_region[0], photo_region[1], (0, 0, 255))
    draw_region(frame, center_region[0], center_region[1], (0, 255, 0))
    # draw_region(frame)
    cv2.imshow('Tracking', frame)

    # Slow the FPS
    cv2.waitKey(10)

    vid_writer.write(frame.astype(np.uint8))
    misc_time = time() - misc_start
    all_time = time() - all_start

    print('-'*30)
    print('All fps :', 1 / all_time)
    print('Det fps :', 1 / det_time)
    # print('---')
    # print('All time:', all_time)
    # print('Cap time:', cap_time)
    # print('Det time:', det_time)
    # print('Trk time:', track_time)
    # print('Msc time:', misc_time)


  # When everything done, release the capture
  cap.release()
  cv2.destroyAllWindows()


if __name__ == "__main__":
  main()
