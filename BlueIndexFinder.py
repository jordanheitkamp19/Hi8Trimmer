import os
import sys
import cv2
import math
import time
from moviepy.editor import *
import datetime

FRAME_SIZE = (480, 640)
FRAME_RATE = 29.97
SAVE_DIRECTORY = "C:/Users/Jordan/ProgrammingProjects/Hi8Processor/FinishedVideos/"
START_DIRECTORY = "D:\Hi8Tapes"
VIDEO_EXTENSION = ".mpg"
NEW_VIDEO_CODEC = "libx264"

FRAME_NAME = "app"
TIMESTAMP_FORMAT = '%H:%M:%S'

#log - prints the passed message with a prepended timestamp
#param: {String} message - string to print to the console
def log( message ):
    print( "[" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "] - " + message )

#convertFrameToSeconds - converts the frame index to how many seconds into the video the frame occurs
#param: {Integer} frameIndex - the current frame index of the video
#param: {Boolean} isEndTime - whether the frameIndex is for the start time or end time of a video
#return: {Integer} - the number of seconds into the video the frame index occurs
def convertFrameToSeconds( frameIndex ):
    return frameIndex / FRAME_RATE

#createMPGForSaving - extracts the time between the start and end frame from the original video
#param: {String} original_video - path to the video being trimmed
#param: {Integer} start_frame - the first frame in the subclip
#param: {Integer} end_frame - the last frame in the subclip
#param: {Integer} last_clip_end_frame - the last frame of the previously saved clip
#param: {Boolean} is_end_of_video - whether or not the end_frame is the last frame of the original video
#return: {MoviePy.VideoFileClip} subclip - the segment of the video between start_frame and end_frame
def createMPGForSaving( original_video, start_frame, end_frame, is_end_of_video=False ):
    start_time = convertFrameToSeconds( start_frame )

    clip = VideoFileClip( original_video, target_resolution=FRAME_SIZE )

    end_time = convertFrameToSeconds( end_frame ) if not is_end_of_video else clip.duration

    subclip = clip.subclip( start_time, end_time )
    log( str( time.strftime( TIMESTAMP_FORMAT, time.gmtime( subclip.duration ) ) ) + " long video found" )

    return subclip

#saveFinalMPGToFile - saves all the discovered clips into one video
#param: {[MoviePy.VideoFileClip]} clips - discovered VideoFileClips
#param: {String} original_filename - path to the video being trimmed
#return: {Boolean} - whether or not the video was successfully written
def saveFinalMPGToFile( clips, original_filename ):
    log( "Concatenating Video Clips..." )
    starttime = time.time()

    if len( clips ) > 1:
        final_video = concatenate_videoclips( clips )
    elif len( clips ) == 1:
        final_video = clips[ 0 ]
    else:
        return False

    for clip in clips:
        clip.close()

    if not os.path.exists( SAVE_DIRECTORY ):
        os.mkdir( SAVE_DIRECTORY )

    log( "Writing " + str( time.strftime( TIMESTAMP_FORMAT, time.gmtime( final_video.duration ) ) ) + " long video clip" )

    final_video.write_videofile( os.path.join( SAVE_DIRECTORY, original_filename + VIDEO_EXTENSION ), codec=NEW_VIDEO_CODEC, threads=3 )

    final_video.close()

    endtime = time.time()
    log( "Video clip saved. Write time: " + str( round( endtime - starttime, 2 ) ) + " seconds" )
    return True

#isFrameScene - determines whether or not the frame is a scene - actual image detailing
#param: {Image} frame - the image to determine to be a scene or not
#return: {Boolean, Boolean} is_blue_frame, is_black_frame - if the frame is all blue, if the frame is all black
def isFrameScene( frame ):
    cv2.imshow(FRAME_NAME, frame)
    mean, std = cv2.meanStdDev( frame )
    avg_std = ( std[ 0 ] + std[ 1 ] + std[ 2 ] ) / 3
    avg_std = avg_std[ 0 ]

    b = mean[ 0 ]
    g = mean[ 1 ]
    r = mean[ 2 ]

    is_blue = b > 180 and g < 10 and r < 10

    is_suspect_scene = avg_std < 30
    return ( not is_blue ), is_suspect_scene

#convertFrameToTimestamp - gets the timestamp of the frame in the video
#param {Integer} frameIndex - the current frame of the video
#param {Boolean} isEndTime - whether or not the frameIndex is for the start or end of the video
#return {String} frame_timestamp - the timestamp of the frame in the video
def convertFrameToTimestamp( frameIndex ):
    frame_time_in_seconds = convertFrameToSeconds( frameIndex )
    frame_timestamp = time.strftime( TIMESTAMP_FORMAT, time.gmtime( frame_time_in_seconds ) )

    return str( frame_timestamp )

if __name__ == "afd":
    HOME = "C:/Users/Jordan/ProgrammingProjects/Hi8Processor/"
    filelist = os.listdir( HOME )

    for filename in filelist[:]:
        print( filename )
        if ".png" in filename:
            is_not_blue, is_suspect = isFrameScene( cv2.imread( os.path.join( HOME, filename ) ) )

#main entry point - finds and removes all blue screens from a directory of videos
if __name__ == "__main__":
    filelist = os.listdir( START_DIRECTORY )

    for filename in filelist[:]:
        if VIDEO_EXTENSION in filename:
            start_frame = -1
            current_frame = 0
            scene_count = 0
            estimated_time = 0
            suspect_frame_count = 0
            last_clip_end_frame = -1
            clips = []

            log( "Starting file: " + filename )
            current_file = os.path.join( START_DIRECTORY, filename )
            current_filebase = filename.split( '.' )[ 0 ]
            capture = cv2.VideoCapture( current_file )

            if filename is None:
                break

            while True:
                _, frame = capture.read()
                if frame is None:
                    break

                is_not_solid, is_suspect = isFrameScene( frame )

                if is_not_solid and start_frame == -1 and not is_suspect: #start of a scene
                    log( "Scene Start" )
                    start_frame = current_frame
                    black_frame_count = 0
                elif start_frame != -1 and ( not is_not_solid or ( suspect_frame_count > 180 and is_suspect ) ): #end of a scene
                    if current_frame - start_frame > FRAME_RATE:
                        scene_count = scene_count + 1
                        log( "Scene Start Time: " + convertFrameToTimestamp( start_frame ) + ", Scene End Time: " + convertFrameToTimestamp( current_frame ) )

                        start_frame = max( start_frame, last_clip_end_frame )
                        clips.append( createMPGForSaving( current_file, start_frame, current_frame, False ) )
                        last_clip_end_frame = current_frame
                    else:
                        log( "Cancelling scene" )

                    start_frame = -1
                    suspect_frame_count = 0
                elif is_suspect:
                    suspect_frame_count = suspect_frame_count + 1

                if current_frame % 21600 == 0:
                    log( str( current_frame ) + " frames completed" )

                if cv2.waitKey(1) & 0xFF == ord( '1' ):
                    break

                current_frame = current_frame + 1

            if start_frame != -1:
                start_frame = max( start_frame, last_clip_end_frame )
                clips.append( createMPGForSaving( current_file, start_frame, current_frame - 1, True ) )

            capture.release()
            log( "Total Scenes: " + str( scene_count ) )
            cv2.destroyWindow( FRAME_NAME )

            if not saveFinalMPGToFile( clips, current_filebase ):
                log( "No clips were found" )

            if cv2.waitKey(1) & 0xFF == ord( '1' ):
                break
        else:
            log( filename + " is not of the correct file type" )
