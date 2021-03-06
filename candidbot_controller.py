import cv2
import numpy as np
import os
import time

from picamera import PiCamera

from vision.detection.yolov3.yolov3_detector import YOLOv3Detector
from vision.tracking.tracker import Tracker
from vision.visualize import draw_tracks, draw_region

from motion_controller import MotionController

from drive_uploader import DriveUploader

# TODO: Faster object detector
# TODO: Figure out how to run command via ssh and have window show up on pi display
# TODO: Figure out how to exit full-screen display with just mouse


class CandidbotController:
  def __init__(self):
    self.frame_height = 480
    self.frame_width = 800

    self.detector = YOLOv3Detector()
    # self.tracker = Tracker(160, 30, 5, 100)  # TODO: Sub in higher max_frames_to_skip when we have a higher fps detector.
    self.tracker = Tracker(250, 2, 3, 100)
    self.camera = PiCamera(resolution=(self.frame_width, self.frame_height))
    # camera.start_preview()  # Displays camera output

    self.motion_controller = MotionController()

    # Spend max_search_frames looking for a target before moving to a new position
    self.search_frames = 0
    self.max_search_frames = 4

    # The threshold from the bottom of the frame inside which we consider a target close enough to
    # photograph
    self.dist_thresh = int(self.frame_height / 2.5)
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
    work_frame = frame.copy()

    self.update_detector_and_tracker(work_frame)

    if debug_display:
      # Draw navigation regions
      center_x = int(self.frame_width / 2)
      photo_region = ((0, 0), (self.frame_width, self.dist_thresh))
      center_region = (
        (center_x - self.center_thresh, 0), (center_x + self.center_thresh, self.frame_height))

      draw_region(work_frame, photo_region[0], photo_region[1], (0, 0, 255))
      draw_region(work_frame, center_region[0], center_region[1], (0, 255, 0))

      # Draw green circle on target
      if self.tracker.target:
        left, top, width, height = self.tracker.target.box
        center_x = int(left + (width / 2))
        center_y = int(top + (height / 2))
        cv2.circle(work_frame, (center_x, center_y), 10, (0, 255, 0), -1)

    cv2.imshow(self.window_name, work_frame)
    cv2.waitKey(10)

    if self.tracker.target is None:
      print(self.search_frames)
      if self.search_frames > self.max_search_frames:
        print('search too long')
        self.motion_controller.turn_90()
        self.search_frames = 0
      else:
        self.search_frames += 1
    else:
      self.search_frames = 0

      if self.should_take_photo():
        self.motion_controller.stop()
        time.sleep(1)

        self.take_photo(frame)

        self.motion_controller.turn_90()
        self.tracker.reset()
      else:
        self.move_to_target()

  def update_detector_and_tracker(self, frame):
    all_start = time.time()
    det_start = time.time()
    box_preds, _ = self.detector.detect_img(frame)
    det_time = time.time() - det_start

    track_start = time.time()
    self.tracker.Update(box_preds)
    track_time = time.time() - track_start

    misc_start = time.time()
    draw_tracks(frame, self.tracker)

    misc_time = time.time() - misc_start
    all_time = time.time() - all_start

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
    _, top, _, _ = self.tracker.target.box

    return top < self.dist_thresh

  def take_photo(self, frame):
    # The camera will already be active, so just save the current frame instead of "taking" another
    # photo?
    # TODO: Photo countdown / graphics to show that a photo was taken?
    # Display flash
    flash_frame = frame.copy()
    cv2.putText(flash_frame, 'TAKING PHOTO', (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
    cv2.imshow(self.window_name, flash_frame)
    cv2.waitKey(20)
    cv2.imshow(self.window_name, frame)

    file_path = os.path.join('saved-photos', str(time.time()).replace('.', '-') + '.jpg')
    # self.camera.capture(file_path)  # This causes an error
    cv2.imwrite(file_path, frame)
    print('Saved photo to %s' % file_path)
    self.uploader.upload(file_path)

  def move_to_target(self):
    frame_center = self.frame_width / 2
    left_thresh = frame_center - self.center_thresh
    right_thresh = frame_center + self.center_thresh

    target_x = self.tracker.get_centroid(self.tracker.target.box)[0]

    # if self.motion_controller.proximity_warning_center():
    #   self.motion_controller.go_backward()
    #   self.motion_controller.turn_90()
    # elif self.motion_controller.proximity_warning_left():
    #   self.motion_controller.go_backward()
    #   self.motion_controller.turn_right()
    # elif self.motion_controller.proximity_warning_right():
    #   self.motion_controller.go_backward()
    #   self.motion_controller.turn_left()


    if target_x < left_thresh:
      # turn_right()
      self.motion_controller.turn_right()
    elif target_x > right_thresh:
      # turn_left()
      self.motion_controller.turn_left()
    else:
      print('move_to_target go forward')
      self.motion_controller.go_forward()

  def nav_continuous(self):
    # TODO: work directly with a file buffer instead of saving/loading to disk if this is a bottleneck
    for file_path in self.camera.capture_continuous('/tmp/{timestamp}.jpg'):
      try:
        frame = cv2.imread(file_path)[:, ::-1, :]
        self.handle_frame(frame)
        os.remove(file_path)
      except KeyboardInterrupt:
        self.motion_controller.close()
        exit(0)

  def nav_test(self):
    print('forward')
    self.motion_controller.go_forward()
    time.sleep(1)
    print('left')
    self.motion_controller.turn_left()
    time.sleep(1)
    print('forward')
    self.motion_controller.go_forward()
    time.sleep(1)
    print('right')
    self.motion_controller.turn_right()
    time.sleep(1)
    print('forward')
    self.motion_controller.go_forward()
    time.sleep(1)
    print('90')
    self.motion_controller.turn_90()
    time.sleep(1)
    print('90')
    self.motion_controller.turn_90()
    time.sleep(1)
    print('stop')
    self.motion_controller.stop()
