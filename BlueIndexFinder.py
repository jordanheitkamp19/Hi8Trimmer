import os
import sys
import cv2
import numpy as np

FRAME_RATE = 16

def isFrameScene( frame ):
    mean, std = cv2.meanStdDev( frame )
    print( mean )
    print( std )

if __name__ == "__main__":
    start_frame = -1
    current_frame = 0

    if os.path.exists( sys.argv[ 1 ] ) && os.path.isfile( sys.argv[ 1 ] ):
        capture = cv2.VideoCapture( sys.argv[ 1 ] )

        while True:
            _, frame = capture.read()
            if frame is None:
                break



            if cv2.waitKey(1) & 0xFF == ord( '1' ):
                break

        capture.release()
