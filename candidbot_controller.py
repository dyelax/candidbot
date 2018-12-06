import cv2
import numpy as np
import os
from time import time

from picamera import PiCamera

from vision.detection.yolov3.yolov3_detector import YOLOv3Detector
from vision.tracking.tracker import Tracker
from vision.visualize import draw_tracks, draw_region

from motion_controller import \
  turn_left, turn_right, turn_90, go_forward, go_backward, \
  proximity_warning_center, proximity_warning_left, proximity_warning_right

from drive_uploader import DriveUploader


class CandidbotController:
  def __init__(self):
    self.frame_height = 480
    self.frame_width = 800

    self.detector = YOLOv3Detector()
    self.tracker = Tracker(160, 30, 5, 100)
    self.camera = PiCamera(resolution=(self.frame_width, self.frame_height))
    # camera.start_preview()  # Displays camera output

    self.target = None  # The track we want to take a picture of

    # The threshold from the bottom of the frame inside which we consider a target close enough to
    # photograph
    self.dist_thresh = self.frame_height / 8
    # The threshold on either side of the frame center inside which we consider an target "centered"
    self.center_thresh = self.frame_width / 6

    self.uploader = DriveUploader()

    # Set up a fullscreen display to show camera output.
    self.window_name = 'display-window'
    cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

  def handle_frame(self, frame, debug_display=True):
    print(frame.shape)
    # If we aren't showing debug display, show the frame before detector and tracker annotations are
    # added. Otherwise, show the frame after they are added.
    if not debug_display:
      # Draw navigation regions
      center_x = int(self.frame_width / 2)
      photo_region = (
        (0, self.frame_height - self.dist_thresh), (self.frame_width, self.frame_height))
      center_region = (
        (center_x - self.center_thresh, 0), (center_x + self.center_thresh, self.frame_height))

      draw_region(frame, photo_region[0], photo_region[1], (0, 0, 255))
      draw_region(frame, center_region[0], center_region[1], (0, 255, 0))
      cv2.imshow(self.window_name, frame)
      cv2.waitKey(10)

    self.update_detector_and_tracker(frame)

    if debug_display:
      cv2.imshow(self.window_name, frame)
      cv2.waitKey(10)

    if self.target is None:
      if len(self.tracker.tracks) > 0:
        self.target = np.random.choice(self.tracker.tracks)
      else:
        turn_90()
    else:
      if self.should_take_photo():
        self.take_photo()
        self.target = None
      else:
        self.move_to_target()

  def update_detector_and_tracker(self, frame):
    all_start = time()
    det_start = time()
    box_preds, _ = self.detector.detect_img(frame)
    det_time = time() - det_start

    track_start = time()
    self.tracker.Update(box_preds)
    track_time = time() - track_start

    misc_start = time()
    draw_tracks(frame, self.tracker)

    misc_time = time() - misc_start
    all_time = time() - all_start

    print('-' * 30)
    print('All fps :', 1 / all_time)
    print('Det fps :', 1 / det_time)
    # print('---')
    # print('All time:', all_time)
    # print('Cap time:', cap_time)
    # print('Det time:', det_time)
    # print('Trk time:', track_time)
    # print('Msc time:', misc_time)

  def should_take_photo(self):
    left, top, width, height = self.target.box
    box_bottom = top + height
    dist = self.frame_height - box_bottom

    return dist < self.dist_thresh

  def take_photo(self, frame):
    # The camera will already be active, so just save the current frame instead of "taking" another
    # photo?
    # TODO: Photo countdown?
    file_path = os.path.join('/tmp', 'candidbot', 'photos', str(time()).replace('.', '-') + '.jpg')
    # self.camera.capture(file_path)  # This causes an error
    cv2.imwrite(file_path, frame)
    # self.uploader.upload(file_path)  # TODO: Turn back on uploading

  def move_to_target(self):
    frame_center = self.frame_width / 2
    left_thresh = frame_center - self.center_thresh
    right_thresh = frame_center + self.center_thresh

    target_x = self.tracker.get_centroid(self.target.box)[0]

    if proximity_warning_center():
      go_backward()
      turn_90()
    elif proximity_warning_left():
      go_backward()
      turn_right()
    elif proximity_warning_right():
      go_backward()
      turn_left()
    elif target_x < left_thresh:
      turn_right()
    elif target_x > right_thresh:
      turn_left()
    else:
      go_forward()

  def nav_continuous(self):
    # TODO: work directly with a file buffer instead of saving/loading to disk if this is a bottleneck
    for file_path in self.camera.capture_continuous('/tmp/{timestamp}.jpg'):
      frame = cv2.imread(file_path)
      self.handle_frame(frame)
      os.remove(file_path)

  def nav_test(self):
    while True:
      go_forward()
      turn_left()
      go_forward()
      turn_right()
      go_forward()
      turn_90()
      turn_90()
