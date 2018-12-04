from mvnc import mvncapi as mvnc


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

    print(graph)