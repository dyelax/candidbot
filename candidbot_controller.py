import cv2
import numpy as np
import os
from time import time

from picamera import PiCamera

from vision.detection.yolov3.yolov3_detector import YOLOv3Detector
from vision.tracking.tracker import Tracker
from vision.visualize import draw_tracks, draw_region

from motion_controller import MotionController

from drive_uploader import DriveUploader

"""
Decrease number of keep frames for tracker
More fluid movement
"""


class CandidbotController:
  def __init__(self):
    self.frame_height = 480
    self.frame_width = 800

    self.detector = YOLOv3Detector()
    self.tracker = Tracker(160, 30, 5, 100)
    self.camera = PiCamera(resolution=(self.frame_width, self.frame_height))
    # camera.start_preview()  # Displays camera output

    self.motion_controller = MotionController()

    self.target = None  # The track we want to take a picture of

    # Spend max_search_frames looking for a target before moving to a new position
    self.search_frames = 0
    self.max_search_frames = 4

    # The threshold from the bottom of the frame inside which we consider a target close enough to
    # photograph
    self.dist_thresh = int(self.frame_height / 20)
    # The threshold on either side of the frame center inside which we consider an target "centered"
    self.center_thresh = int(self.frame_width / 6)

    self.uploader = DriveUploader()

    # Set up a fullscreen display to show camera output.
    self.window_name = 'display-window'
    cv2.namedWindow(self.window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

  def handle_frame(self, frame, debug_display=True):
    # If we aren't showing debug display, show the frame before detector and tracker annotations are
    # added. Otherwise, show the frame after they are added.
    if not debug_display:
      cv2.imshow(self.window_name, frame)
      cv2.waitKey(10)

    self.update_detector_and_tracker(frame)

    if debug_display:
      # Draw navigation regions
      center_x = int(self.frame_width / 2)
      photo_region = (
        (0, self.frame_height - self.dist_thresh), (self.frame_width, self.frame_height))
      center_region = (
        (center_x - self.center_thresh, 0), (center_x + self.center_thresh, self.frame_height))

      draw_region(frame, photo_region[0], photo_region[1], (0, 0, 255))
      draw_region(frame, center_region[0], center_region[1], (0, 255, 0))

      # Draw green circle on target
      if self.target:
        left, top, width, height = self.target.box
        center_x = int(left + (width / 2))
        center_y = int(top + (height / 2))
        cv2.circle(frame, (center_x, center_y), 20, (0, 255, 0), -1)

      cv2.imshow(self.window_name, frame)
      cv2.waitKey(10)

    if self.target is None:
      if len(self.tracker.tracks) > 0:
        self.target = np.random.choice(self.tracker.tracks)
        self.search_frames = 0
      elif self.search_frames > self.max_search_frames:
        self.motion_controller.turn_90()
        self.search_frames = 0
      else:
        self.search_frames += 1
    else:
      if self.should_take_photo():
        self.take_photo(frame)
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
    file_path = os.path.join('saved-photos', str(time()).replace('.', '-') + '.jpg')
    # self.camera.capture(file_path)  # This causes an error
    cv2.imwrite(file_path, frame)
    print('Saved photo to %s' % file_path)
    # self.uploader.upload(file_path)  # TODO: Turn back on uploading

  def move_to_target(self):
    frame_center = self.frame_width / 2
    left_thresh = frame_center - self.center_thresh
    right_thresh = frame_center + self.center_thresh

    target_x = self.tracker.get_centroid(self.target.box)[0]

    if self.motion_controller.proximity_warning_center():
      self.motion_controller.go_backward()
      self.motion_controller.turn_90()
    elif self.motion_controller.proximity_warning_left():
      self.motion_controller.go_backward()
      self.motion_controller.turn_right()
    elif self.motion_controller.proximity_warning_right():
      self.motion_controller.go_backward()
      self.motion_controller.turn_left()
    elif target_x < left_thresh:
      # turn_right()
      self.motion_controller.turn_left()
    elif target_x > right_thresh:
      # turn_left()
      self.motion_controller.turn_right()
    else:
      self.motion_controller.go_forward()

  def nav_continuous(self):
    # TODO: work directly with a file buffer instead of saving/loading to disk if this is a bottleneck
    for file_path in self.camera.capture_continuous('/tmp/{timestamp}.jpg'):
      frame = cv2.imread(file_path)
      self.handle_frame(frame)
      os.remove(file_path)

  def nav_test(self):
    while True:
      self.motion_controller.go_forward()
      self.motion_controller.turn_left()
      self.motion_controller.go_forward()
      self.motion_controller.turn_right()
      self.motion_controller.go_forward()
      self.motion_controller.turn_90()
      self.motion_controller.turn_90()
