import cv2
import numpy as np


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


def draw_region(frame, top_left, bottom_right, color):
  overlay = np.zeros_like(frame)
  cv2.rectangle(overlay, top_left, bottom_right, color, -1)

  cv2.addWeighted(frame, 1, overlay, 0.5, 0, frame)

