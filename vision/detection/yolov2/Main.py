from mvnc import mvncapi as mvnc
import cv2
import numpy as np
from time import time

if __name__ == '__main__':
  # grab a list of all NCS devices plugged in to USB
  print("[INFO] finding NCS devices...")
  devices = mvnc.enumerate_devices()

  # if no devices found, exit the script
  if len(devices) == 0:
    print("[INFO] No devices found. Please plug in a NCS")
    quit()

  # use the first device since this is a simple test script
  print("[INFO] found {} devices. device0 will be used. "
        "opening device0...".format(len(devices)))
  device = mvnc.Device(devices[0])
  device.open()

  # open the CNN graph file
  print("[INFO] loading the graph file into RPi memory...")
  with open('yolov2.graph', mode="rb") as f:
    graph_in_memory = f.read()

  # load the graph into the NCS
  print("[INFO] allocating the graph on the NCS...")
  graph = mvnc.Graph('YOLOv2')
  graph.allocate(device, graph_in_memory)

  input_fifo, output_fifo = graph.allocate_with_fifos(
    device, graph_in_memory,
    input_fifo_type=mvnc.FifoType.HOST_WO,
    input_fifo_num_elem=30,
    input_fifo_data_type=mvnc.FifoDataType.FP32,
    output_fifo_type=mvnc.FifoType.HOST_RO,
    output_fifo_num_elem=30,
    output_fifo_data_type=mvnc.FifoDataType.FP32
  )

  print(graph)

  image = cv2.imread('../../../test/test1.jpg')
  # image = image_orig.copy()
  image = cv2.resize(image, (416, 416))
  image = image.astype(np.float32)
  for i in range(30):
    start = time()
    graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, image, None)
    (preds, userobj) = output_fifo.read_elem()
    end = time()

    print("[INFO] inference took {:.5} seconds".format(end - start))

    print(len(preds))
    print(preds)

  # clean up the graph and device
  input_fifo.destroy()
  output_fifo.destroy()
  graph.destroy()
  device.close()
  device.destroy()
