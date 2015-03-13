HOW TO INSTALL:

Note: This only works on Macs.

First, you need OpenCV with Python. To install this, follow the instructions at: https://jjyap.wordpress.com/2014/05/24/installing-opencv-2-4-9-on-mac-osx-with-python-support/

Then you need Qt and Pyside. To install these, follow the instructions at:  https://pypi.python.org/pypi/PySide#installing-pyside-on-a-mac-os-x-system

Or, download PySide 1.2.1 and Qt 4.8 here (may not work on newer versions of OS X): http://qt-project.org/wiki/PySide_Binaries_MacOSX




HOW TO RUN:

# All our necessary code is in this directory
cd … /FinalCode

# Run Video Application with live video from webcam
python face_video.py

# Run Image Application
# Will edit photo saved as screenshot.jpg in current directory
python face_window.py

# Groucho glasses simple demo
python groucho_demo.py

# Tracking test code
python livetrackwithface.py




TUNING PARAMETERS (optional - in video.py):

The Video class used for tracking takes in several variables used to tune tracking performance. Those variables are input into the video class in the form of a list containing all of the following in order:
minRemovalScore - the minimum score necessary to be matched to a certain face
timeOut - the number of seconds until a face is considered to have permanently left the frame
cleanThresh - the number of frames a face must have been consecutively detected before it is no longer considered a “ghost face”
binNumber - number of bins in the histogram for the color profile
distanceWeight - the weight on the change in distance score
timeWeight - the weight on the change in time score
sizeWeight - the weight on the change in size (width) score
weights = (distanceWeight, timeWeight, sizeWeight)
writingToFiles - True if you want .csv variable output, False otherwise
distDev - maximum tolerable change in distance. The value at which the score for change in position goes below 0.25
timeDev - maximum tolerable change in time. The value at which the score for change in time goes below 0.25
sizeDev maximum tolerable change in size (width). The value at which the score for change in size goes below 0.25
devs = (distDev, timeDev, sizeDev)
framesback - number of frames to look back at for Kalman filter corrections
These variables must be input as variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles, devs, framesback]
The default values of these variables are [0.25, 15, 100, (0.5, 0, 0.5), False, (200.0, 0.34, 0.25), 2]

The file livetrackwithface.py can be used as a simple interface for changing these variables without having to run the entire application. The user must note that performance will not necessarily be the same for livetrackwithface.py and the full application, but track performance should be comparable.