import os
import cv2
import time
import psutil
import logging
import pandas as pd
import numpy as np
import multiprocessing as mp
from collections import Counter
from deepface import DeepFace
import subprocess
import config

# =============================================================================
# Environment Setup & Global Variables
# =============================================================================
# Global error counter
error_counter = Counter()

# Define directories relative to the current working directory using config.py settings.
BASE_DIR = os.getcwd()
VIDEO_DIR = os.path.join(BASE_DIR, config.VIDEO_PATH)              # Folder with video files
ANALYSIS_DIR = os.path.join(BASE_DIR, config.ANALYSIS_DIR)         # Folder for analysis outputs
LOG_DIR = os.path.join(BASE_DIR, config.LOG_DIR)                   # Folder for per-video log files
CSV_DIR = os.path.join(ANALYSIS_DIR, config.CSV_DIR)               # Folder for CSV files
EXCEL_DIR = os.path.join(ANALYSIS_DIR, config.EXCEL_DIR)           # Folder for Excel files

# Create directories if they don't exist yet.
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

# Build the DeepFace model (default is OpenFace, please adjust in the config.py file).
# Other options are: Facenet, VGG-Face, DeepID, ArcFace, GhostFaceNet.
# DeepFace does allow for more models but they have not been easy to implement.
emotion_model = DeepFace.build_model(config.EMOTION_MODEL)

# Configuration of logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "analysis.log")),
        logging.StreamHandler()
    ]
)

# =============================================================================
# Helper Functions
# =============================================================================
def get_num_processes():
    """
    Function to determine the number of processes to use for parallel processing.
    
    Returns:
        int: The number of simultaneous processes defined in the config.py file 
             (config.POOL_SIZE) or 4 if not defined.
    """
    processes = config.POOL_SIZE
    return processes if processes else 4


def analyse_video(video_path, frame_step=1):
    """
    Wrapper function to process a single video file.
    It extracts the 'source' identifier from the video's filename,
    prepares the output CSV (and Excel) file path, and then calls
    analyse_video_internal with the correct parameters.
    Args:
        video_path (str): Full path to the video file.
        frame_step (int): Analyse every n-th frame.
    Returns:
        DataFrame or None: The analysis DataFrame (with an added 'source' column) or None on failure.
    """
    # Extract the base name of the video (without extension) to use as the source identifier.
    source = os.path.splitext(os.path.basename(video_path))[0]
    # Construct the output CSV file path in the analysis folder.
    output_csv = os.path.join(CSV_DIR, f"{source}_emotional_analysis.csv")
    excel_file = os.path.join(EXCEL_DIR, f"{source}_emotional_analysis.xlsx")
    # Optionally, you might also want to create a per-video log file here if desired.
    return analyse_video_internal(video_path, output_csv, excel_file, source, frame_step)


def get_dominant_emotion(emo):
    """
    Return the dominant emotion if its confidence is above the threshold defined 
    in config.EMOTION_SCORE_THRESHOLD, else a message indicating no dominant
    emotion has been detected.
    
    Args:
        emo (dict): The emotions determined by DeepFace.
    Returns:
        str: The dominant emotion or a message indicating no dominant emotion detected.
    """
    if not emo:
        return 'no emotion detected'
    dominant = max(emo, key=emo.get)
    return dominant if emo[dominant] >= config.EMOTION_SCORE_THRESHOLD else 'no dominant emotion detected'



# Global variable for the preloaded model
global_model = None

# Initialiser of each worker / subprocess
def init_worker(backend_model):
    """Initialize each worker with a preloaded model."""
    global global_model
    global_model = backend_model


def analyse_emotion_multiproc(args):
    """
    Analyse a single frame using the preloaded DeepFace model.
    Args:
        args (tuple): Contains (frame, frame_number, backend).
    Returns:
        tuple: (analysis_dict, candidate_dominant_emotion, error message)
    """
    frame, frame_number, backend = args
    # Check for an empty frame.
    if frame is None or frame.size == 0 or frame.shape[0] == 0 or frame.shape[1] == 0:
        return None, None, f'Invalid frame at frame number {frame_number}.'
    try:
        # Perform DeepFace analysis using the preloaded model.
        analysis = DeepFace.analyze(
            img_path=frame,
            actions=['emotion'],
            enforce_detection=False,
            detector_backend=backend
        )
        emotions = analysis[0].get('emotion', {})
        # Determine the candidate dominant emotion.
        candidate = max(emotions, key=emotions.get)
        # Attach frame_number and face_confidence for downstream use.
        analysis[0]['frame_number'] = frame_number
        # Return the analysis result and candidate; let get_dominant_emotion decide final output.
        return analysis[0], candidate, None
    except Exception as e:
        logging.error(f'Error analysing frame {frame_number} with backend {backend}: {e}')
        error_counter['first_backend_error'] += 1
        return None, None, f'Error in analysis in frame {frame_number} with {backend}'


# =============================================================================
# Video Analysis Functions
# =============================================================================
def analyse_video_internal(video_path, output_csv, excel_file, source, frame_step):
    """
    Processes one video file: opens the video, samples frames at the specified rate,
    runs DeepFace analysis on each selected frame using multiprocessing,
    builds a DataFrame with the results, and saves both CSV and Excel files.
    
    Args:
        video_path (str): Path to the video file to analyze
        output_csv (str): Path where to save the CSV results
        excel_file (str): Path where to save the Excel results
        source (str): Identifier for the video source (typically the filename without extension)
        frame_step (int): Analyze every n-th frame
        
    Returns:
        DataFrame or None: The analysis results as a DataFrame, or None if processing failed
    
    Logs detailed timing information and analysis statistics.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Error: Could not open video {video_path}.")
        return None

    # Record the start time for this video.
    start_time = time.time()
    logging.info(f"Started processing video {video_path} at {time.ctime(start_time)}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
    tasks = []
    frame_number = 0
    total_frames = 0

    # Collect frames for analysis based on the frame step.
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        total_frames += 1
        if frame_number % frame_step == 0:
            tasks.append((frame, frame_number, 'opencv'))
        frame_number += 1
        if frame_number % 1000 == 0:
            interim_time = time.time()
            logging.info(f"Read frame {frame_number} of input video after {interim_time - start_time:.2f} seconds")
    cap.release()

    logging.info(f"Video {video_path} has {total_frames} frames; frame step: {frame_step}; {len(tasks)} frames to analyse.")

    # Use multiprocessing with progress tracking.
    num_processes = get_num_processes()
    logging.info(f"Using {num_processes} processes for processing.")
    manager = mp.Manager()
    progress_counter = manager.Value('i', 0)  # Shared progress counter
    lock = manager.Lock()  # Explicit lock for synchronization
    total_tasks = len(tasks)

    def update_progress(result):
        # Callback function to update progress.
        nonlocal progress_counter
        with lock:  # Use the explicit lock
            progress_counter.value += 1
            current_progress = progress_counter.value
            if current_progress % max(1, total_tasks // 10) == 0:  # Log every 10%
                elapsed_time = time.time() - start_time
                logging.info(
                    f"Processed {current_progress}/{total_tasks} frames ({current_progress / total_tasks * 100:.1f}%), Elapsed Time: {elapsed_time:.1f}s"
                )

    # Start timing the analysis phase
    analysis_start_time = time.time()
    results = []
    analysed_frames = 0
    unsuccessful_retries = 0

    with mp.Pool(processes=num_processes, initializer=init_worker, initargs=(emotion_model,)) as pool:
        for res in pool.imap_unordered(analyse_emotion_multiproc, tasks):
            update_progress(res)  # Update progress
            analysis_dict, emotion, error = res
            if analysis_dict:
                results.append(analysis_dict)
                analysed_frames += 1
            elif error:
                logging.warning(error)
                unsuccessful_retries += 1

    # Record the end time for the analysis phase
    analysis_end_time = time.time()
    analysis_duration = analysis_end_time - analysis_start_time

    # Record the overall end time for this video
    end_time = time.time()
    duration = end_time - start_time
    logging.info(f"Finished processing video {video_path} at {time.ctime(end_time)}; Duration: {duration:.2f} seconds")
    logging.info("Analysis phase took %.2f seconds with the model %s",
                 analysis_duration, emotion_model.__class__.__name__)  # Log the model used

    # Build DataFrame and save results.
    if results:
        df = pd.DataFrame(results)
        if 'emotion' in df.columns:
            df.rename(columns={'emotion': 'raw_output'}, inplace=True)

        # Define the list of emotions.
        emotions_list = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

        # For each emotion column, if face_confidence is below the threshold, set the value to 0.
        for emo in emotions_list:
            df[emo] = df.apply(
                lambda row: row['raw_output'].get(emo, 0) 
                if row['face_confidence'] >= config.FACE_CONFIDENCE_THRESHOLD else 0, 
                axis=1
            )

        # Add the dominant emotion column.
        df['dominant_emotion'] = df.apply(
            lambda row: 'no face detected' 
            if row['face_confidence'] < config.FACE_CONFIDENCE_THRESHOLD 
            else get_dominant_emotion(row['raw_output']), axis=1
        )

        # Base column ordering for individual files.
        columns_order = ['frame_number', 'dominant_emotion'] + emotions_list + ['face_confidence', 'region', 'raw_output']
        columns_order = [col for col in columns_order if col in df.columns]
        df = df[columns_order]

        # Add the source column.
        df['source'] = source

        # Sort by frame_number for individual file export.
        df.sort_values(by="frame_number", inplace=True)

        # Save as CSV.
        df.to_csv(output_csv, index=False)
        # Also save as Excel.
        df.to_excel(excel_file, index=False)

        # Log a summary.
        emotion_counts = {}
        if 'dominant_emotion' in df.columns:
            unique_emotions = df['dominant_emotion'].unique()
            for e in unique_emotions:
                emotion_counts[e] = df['dominant_emotion'].tolist().count(e)

        # Calculate combined count for failures (using both messages)
        no_dominant = emotion_counts.get('no dominant emotion detected', 0)
        no_face = emotion_counts.get('no face detected', 0)
        failures = no_dominant + no_face

        logging.info("Emotion analysis results:")
        for emo, count in emotion_counts.items():
            logging.info(f"{emo}: {count} frames")
        logging.info(f"Total frames: {total_frames}")
        logging.info(f"Frame count: {frame_count}")
        logging.info(f"Frame rate: {frame_rate} FPS")
        logging.info(f"Analysed frames: {analysed_frames}")
        logging.info(f"Frames with no dominant emotion detected (failure): {failures}")
        logging.info(f"Unsuccessful retries: {unsuccessful_retries}")
        logging.info(f"Backend error {error_counter['first_backend_error']}")
        logging.info("Analysis completed.")
        return df
    else:
        logging.error("No analysis results to process.")
        return None
    

def process_all_videos(frame_step=1):
    """
    Searches the VIDEO_DIR for video files, processes each one with the specified frame step,
    and then creates combined output files (CSV and Excel) with an added 'source' column.
    Logs timestamps and total durations for each file and for the entire process.
    Args:
        frame_step (int): Analyse every n-th frame.
    """
    overall_start = time.time()
    logging.info(f"Started processing all videos at {time.ctime(overall_start)}")

    video_files = [
        os.path.join(VIDEO_DIR, f)
        for f in os.listdir(VIDEO_DIR)
        if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))
    ]

    if not video_files:
        message = f"No video files found in the folder: {VIDEO_DIR}"
        print(message)
        logging.info(message)
        return

    # Create a list of just the file names (without the full path)
    file_names = [os.path.basename(f) for f in video_files]
    message = f"Found {len(video_files)} video file(s): {file_names}"
    print(message)
    logging.info(message)

    combined_dfs = []
    for video in video_files:
        print(f"Processing {video}...")
        logging.info(f"Processing {video}...")
        # Call the wrapper function that correctly prepares the arguments
        df = analyse_video(video, frame_step=frame_step)
        if df is not None:
            combined_dfs.append(df)

    if combined_dfs:
        combined_df = pd.concat(combined_dfs, ignore_index=True)

        # Sort the combined DataFrame by source first and then by frame_number.
        combined_df.sort_values(by=["source", "frame_number"], inplace=True)

        # Define a standard ordering for the combined file columns.
        emotions_list = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        combined_columns = ["frame_number", "source", "dominant_emotion"] + emotions_list + ["face_confidence", "region", "raw_output"]

        # Only keep columns that are present.
        combined_columns = [col for col in combined_columns if col in combined_df.columns]
        combined_df = combined_df[combined_columns]

        combined_csv = os.path.join(CSV_DIR, "combined_emotional_analysis.csv")
        combined_excel = os.path.join(EXCEL_DIR, "combined_emotional_analysis.xlsx")
        combined_df.to_csv(combined_csv, index=False)
        combined_df.to_excel(combined_excel, index=False)

        message = f"Combined analysis saved to:\n  CSV: {combined_csv}\n  Excel: {combined_excel}"
        print(message)
        logging.info(message)
    else:
        message = "No analysis data to combine."
        print(message)
        logging.info(message)

    overall_end = time.time()
    overall_duration = overall_end - overall_start
    logging.info(
        f"Finished processing all videos with {get_num_processes()} Processes at {time.ctime(overall_end)}; Total duration: {overall_duration:.2f} seconds"
    )
    print(
        f"Total processing time with {get_num_processes()} Processes for all videos: {overall_duration:.2f} seconds (started at {time.ctime(overall_start)}, finished at {time.ctime(overall_end)})."
    )


def run_analysis(frame_step=1):
    """
    Runs the analysis for all videos found in the 'videos' folder,
    using the specified frame step.
    Args:
        frame_step (int): Analyse every n-th frame.
    """
    process_all_videos(frame_step)


if __name__ == '__main__':
    run_analysis()