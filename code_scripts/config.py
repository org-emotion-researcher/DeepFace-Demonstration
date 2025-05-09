import os
import psutil

# The directory containing this config.py file
_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# This is the parent directory of the _SCRIPTS_DIR
PROJECT_ROOT = os.path.dirname(_SCRIPTS_DIR)

# --- Define paths to important folders relative to the PROJECT_ROOT ---
INPUT_VIDEO_DIR = os.path.join(PROJECT_ROOT, "videos for AFEA demonstration")

# Analysis and video input/output settings.
FRAME_STEP = 1 # Analyse every n-th frame. The input through the terminal with sampling_rate can override this.
REQUIREMENTS_PATH = os.path.join(_SCRIPTS_DIR, "requirements.txt")
VIDEO_PATH = INPUT_VIDEO_DIR    # Folder with the input video files to be analysed.
ANALYSIS_DIR = os.path.join(PROJECT_ROOT, "raw data output files")# Folder where analysis CSV/Excel files are saved.
CSV_DIR = os.path.join(ANALYSIS_DIR, "CSV")                          # Folder where the CSV files are saved.
EXCEL_DIR = os.path.join(ANALYSIS_DIR, "Excel")                      # Folder where the Excel files are saved.

# New parent directory for all visualisation outputs
DATA_VISUALISATION_DIR = os.path.join(PROJECT_ROOT, "data visualisation")

PLOTS_DIR = DATA_VISUALISATION_DIR            # Folder where the plots files are saved.
ANIMATIONS_DIR = DATA_VISUALISATION_DIR       # Folder where the animation files and segments are saved.
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")                      # Folder where the log files are saved.

# Thresholds
FACE_CONFIDENCE_THRESHOLD = 0.9     # Confidence threshold for face detection.
EMOTION_SCORE_THRESHOLD = 50        # Threshold for when a emotion is deemed as dominant.
CONFIDENCE_THRESHOLD = 80           # Confidence threshold for emotion detection.
EMOTION_MODEL = "Facenet"           # Defines which facial recognition model is being utilized: OpenFace, Facenet, VGG-Face, 
                                    # DeepID, ArcFace, GhostFaceNet have all been tested and are working 
                                    # after the download of new model weights. 
                                    # DeepFace does allow for more models but they have not been easy to implement.

# Thread and Segmentation settings
CPU_CORES = psutil.cpu_count(logical=False) # Get number of physical CPU cores.
POOL_SIZE = (CPU_CORES) // 4                # We set the pool size to two-thirds the number of CPU cores.
NUM_SEGMENTS = POOL_SIZE * 2                # Number of segments to divide the video into for parallel processing. 
                                            # This will alleviate the load on the CPU and especially the RAM.

# Frame and plot settings.
FRAME_RATE = 30     # Default frame rate (if not read from video).
PLOT_WIDTH = 19.2   # Width of the static plot (in inches).
PLOT_HEIGHT = 5.4   # Height of the static plot (in inches).
PLOT_DPI = 100      # Pixels per inch (dots per inch).