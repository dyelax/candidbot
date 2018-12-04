import argparse
from datetime import datetime

from vision.detection.yolov2.ObjectWrapper import *
from vision.detection.yolov2.Visualize import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', dest='graph', type=str,
                        default='graph', help='MVNC graphs.')
    parser.add_argument('--image', dest='image', type=str,
                        default='./images/dog.jpg', help='An image path.')
    args = parser.parse_args()

    network_blob=args.graph
    imagefile = args.image
    videofile = args.video

    detector = ObjectWrapper(network_blob)
    stickNum = ObjectWrapper.devNum

    # image preprocess
    img = cv2.imread(imagefile)
    start = datetime.now()

    results = detector.Detect(img)

    end = datetime.now()
    elapsedTime = end-start

    print ('total time is " milliseconds', elapsedTime.total_seconds()*1000)

    imdraw = Visualize(img, results)
    # cv2.imshow('Demo',imdraw)
    cv2.imwrite('test.jpg',imdraw)
    cv2.waitKey(10000)
