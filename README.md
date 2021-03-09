# Hi8Trimmer
Python tool to trim the blue frames from videos

The BlueIndexFinder is a tool used to trim the blue frames from videos.
Originally created to remove the blue frames from a digitally converted Hi8 tape.

Usage notes:
You will need to update some of the global variables:

FRAME_SIZE 	- (height, width) of the target frame
FRAME_RATE 	- video frames per second
SAVE_DIRECTORY 	- directory to save the finished videos to
START_DIRECTORY - directory where the raw videos are stored
VIDEO_EXTENSION - extension of the videos: used for saving and loading
NEW_VIDEO_CODEC - codec used to save the videos: see https://zulko.github.io/moviepy/ref/VideoClip/VideoClip.html for more info


P.S. Takes upwards of an hour to trim each video
