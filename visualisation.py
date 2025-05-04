import os
import glob
import multiprocessing
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter
import subprocess
import time
from datetime import datetime
import warnings
import config
import logging
from ffmpeg_installer import ensure_ffmpeg

# Suppress Python deprecation warnings.
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set directories based on config.
BASE_DIR = os.getcwd()
ANALYSIS_DIR = os.path.join(BASE_DIR, config.ANALYSIS_DIR)
LOG_DIR = os.path.join(BASE_DIR, config.LOG_DIR)
CSV_DIR = os.path.join(ANALYSIS_DIR, config.CSV_DIR)
PLOTS_DIR = os.path.join(BASE_DIR, config.PLOTS_DIR)
ANIMATIONS_DIR = os.path.join(BASE_DIR, config.ANIMATIONS_DIR)
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(ANIMATIONS_DIR, exist_ok=True)

# Parameters from config.
FRAME_RATE = config.FRAME_RATE
CONFIDENCE_THRESHOLD = config.CONFIDENCE_THRESHOLD
PLOT_WIDTH = config.PLOT_WIDTH
PLOT_HEIGHT = config.PLOT_HEIGHT
PLOT_DPI = config.PLOT_DPI
NUM_SEGMENTS = config.NUM_SEGMENTS
POOL_SIZE = config.POOL_SIZE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "visualisation.log")),  # Fixed
        logging.StreamHandler()
    ]
)

# Ensure FFmpeg is available for the visualisation
try:
    logging.info("Ensuring FFmpeg is available for the visualisation process...")
    ensure_ffmpeg()
    logging.info("FFmpeg check/setup complete.")
except Exception as e:
    logging.error(f"Failed during ensure_ffmpeg call: {e}")
    # Decide if you want to exit if FFmpeg setup fails
    # sys.exit("Could not ensure FFmpeg is available.")

# Emotion color mapping and renaming.
emotions_colors = {
    'happy':     'orange',
    'sad':       'blue',
    'angry':     'red',
    'surprise': 'yellow',
    'disgust': 'darkgreen',
    'fear':   'black',
    'neutral':   'gray'
}
emotion_rename_map = {
    'happy':     'joy',
    'sad':       'sadness',
    'angry':     'anger',
    'surprise': 'surprise',
    'disgust': 'disgust',
    'fear':   'fear',
    'neutral':   'neutrality'
}

###############################################################################
# Formatter for time ticks on the x-axis.
###############################################################################
def time_formatter_in_seconds(x, pos):
    """
    Format time values (in seconds) as minutes:seconds (M:SS).
    
    Args:
        x (float): Time value in seconds
        pos: Position argument required by matplotlib formatter
    
    Returns:
        str: Formatted time string in M:SS format
    """
    minutes = int(x // 60)
    seconds = int(x % 60)
    return f"{minutes}:{seconds:02d}"

###############################################################################
# PER-SEGMENT FUNCTION for Animation
###############################################################################
def produce_segment(seg_index, segment_start_frame, segment_end_frame, total_frames, all_data):
    """
    Creates one animation segment with local progress tracking.
    
    Args:
        seg_index (int): Index of the segment
        segment_start_frame (int): First frame of the segment
        segment_end_frame (int): Last frame of the segment
        total_frames (int): Total number of frames in the video
        all_data (list): List containing a tuple of (DataFrame, title_string)
    
    Returns:
        bool: True if segment was created successfully, False otherwise
    """
    start_time = time.time()
    try:
        # Generate frame indices for the segment
        segment_frames = np.arange(segment_start_frame, segment_end_frame)
        times = segment_frames / FRAME_RATE

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(PLOT_WIDTH, PLOT_HEIGHT), dpi=PLOT_DPI, constrained_layout=True)
        df, title_str = all_data[0]
        ax.set_title(f"{title_str}", fontsize=12, style='italic', pad=6)
        ax.set_ylabel("Confidence (%)")
        ax.set_ylim(CONFIDENCE_THRESHOLD, 100)
        ax.set_xlim(0, total_frames / FRAME_RATE)
        ax.xaxis.set_major_formatter(FuncFormatter(time_formatter_in_seconds))
        ax.set_xlabel("Time (MM:SS)", fontsize=8)

        # Draw bars for each emotion
        bar_containers = []
        x = df['time_sec'].values
        for emo, color in emotions_colors.items():
            if emo in df.columns:
                y = df[emo].where(df[emo] >= CONFIDENCE_THRESHOLD)
                valid_mask = y.notna()
                if valid_mask.any():
                    bars = ax.bar(x[valid_mask], y[valid_mask],
                                  width=0.1, color=color, alpha=0.5,
                                  edgecolor='none', linewidth=0,
                                  label=emotion_rename_map.get(emo, emo))
                    bar_containers.append(bars)

        # Add legend
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1), borderaxespad=0, frameon=False, fontsize=8)

        # Animation setup
        vline = ax.axvline(times[0], color='black', linestyle='--', linewidth=1.5)
        seg_filename = f"segment_{seg_index}.mp4"
        seg_path = os.path.join(ANIMATIONS_DIR, seg_filename)
        if os.path.exists(seg_path):
            os.remove(seg_path)

        writer = animation.FFMpegWriter(
            fps=FRAME_RATE,
            codec="libx264",
            bitrate=1500,
            extra_args=['-preset', 'fast', '-pix_fmt', 'yuv420p', '-crf', '23']
        )

        # Manual frame generation
        with writer.saving(fig, seg_path, dpi=100):
            fig.canvas.draw()
            background = fig.canvas.copy_from_bbox(fig.bbox)

            for frame_idx, frame in enumerate(segment_frames):
                t = frame / FRAME_RATE  # Convert frame index to timestamp

                # Print local progress every 10% of the segment
                if frame_idx % max(1, len(segment_frames) // 10) == 0:
                    elapsed_time = time.time() - start_time
                    progress = frame_idx / len(segment_frames) * 100
                    print(f"\rSegment {seg_index}: {progress:.1f}% complete, Elapsed Time: {elapsed_time:.1f}s", end="")

                # Update vertical line
                vline.set_xdata([t, t])

                # Restore background and redraw
                fig.canvas.restore_region(background)
                ax.draw_artist(vline)
                fig.canvas.blit(fig.bbox)
                writer.grab_frame()

        plt.close(fig)
        elapsed = time.time() - start_time
        print(f"\n✅ Segment {seg_index} saved ({elapsed:.1f}s)")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Segment {seg_index} failed after {elapsed:.1f}s: {str(e)}")
        if 'fig' in locals():
            plt.close(fig)
        return False

###############################################################################
# STATIC PLOT FUNCTION
###############################################################################
def create_static_plot_for_file(csv_file):
    """
    Reads an individual analysis CSV file and creates a static bar plot.
    
    Args:
        csv_file (str): Path to the CSV file containing emotion analysis data
    
    Returns:
        None
        
    The function creates a plot with time (MM:SS) on the x-axis and emotion
    confidence percentages on the y-axis. Only confidence values above the
    threshold defined in config.CONFIDENCE_THRESHOLD are shown.
    Saves the plot as a PNG in the PLOTS_DIR.
    """
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return
    if 'frame_number' not in df.columns:
        print(f"'frame_number' column missing in {csv_file}, skipping.")
        return
    df.sort_values("frame_number", inplace=True)
    df['time_sec'] = df['frame_number'] / FRAME_RATE
    base_name = os.path.splitext(os.path.basename(csv_file))[0]
    title = base_name.replace("_emotional_analysis", "")
    fig, ax = plt.subplots(figsize=(PLOT_WIDTH, PLOT_HEIGHT), dpi=PLOT_DPI, constrained_layout=True)
    ax.set_title(f"{title}", fontsize=12, style='italic', pad=6)
    ax.set_ylabel("Confidence (%)")
    ax.set_ylim(CONFIDENCE_THRESHOLD, 100)
    ax.set_xlim(0, df['time_sec'].max())
    ax.xaxis.set_major_formatter(FuncFormatter(time_formatter_in_seconds))
    ax.set_xlabel("Time (MM:SS)", fontsize=8)
    ax.xaxis.labelpad = 0
    ax.xaxis.set_label_coords(0.5, -0.05)
    for emo, color in emotions_colors.items():
        if emo in df.columns:
            y = df[emo].where(df[emo] >= CONFIDENCE_THRESHOLD)
            valid_mask = y.notna()
            if valid_mask.any():
                ax.bar(df['time_sec'][valid_mask], y[valid_mask],
                       width=0.1, color=color, alpha=0.5,
                       edgecolor='none', linewidth=0,
                       label=emotion_rename_map.get(emo, emo))
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1), borderaxespad=0, frameon=False, fontsize=8)
    fig.suptitle(f'DeepFace Emotion Evaluation (Confidence Threshold ≥ {CONFIDENCE_THRESHOLD}%)', fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.99], h_pad=0.5, pad=0.3)
    static_plot_path = os.path.join(PLOTS_DIR, f"{base_name}_static.png")
    plt.savefig(static_plot_path)
    plt.close(fig)
    print(f"Static plot saved to: {static_plot_path}")

###############################################################################
# MAIN VISUALISATION FUNCTION
###############################################################################
def run_visualisation(sheet=""):
    """
    Main function to create static plots and animations from emotion analysis data.
    
    Args:
        sheet (str): Optional specific CSV file to process. If empty, processes all CSV files.
    
    Returns:
        None
        
    This function:
    1. Finds all CSV files with emotion analysis data
    2. Creates static plots for each file
    3. Creates segmented animations for each file using multiprocessing
    4. Concatenates segments into a final animation using FFmpeg
    5. Logs timing information throughout the process
    """
    overall_start = time.time()
    if sheet:
        csv_files = [os.path.join(CSV_DIR, sheet)]
    else:
        csv_files = glob.glob(os.path.join(CSV_DIR, "*_emotional_analysis.csv"))
        combined_file = os.path.join(CSV_DIR, "combined_emotional_analysis.csv")
        if combined_file in csv_files:
            csv_files.remove(combined_file)

    if not csv_files:
        print("No analysis CSV files found in the analysis folder.")
        return

    for csv_file in csv_files:
        print(f"Processing file: {csv_file}")

        # Create static plot
        create_static_plot_for_file(csv_file)

        # Create animation for each file
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            continue
        if 'frame_number' not in df.columns:
            print(f"'frame_number' missing in {csv_file}, skipping animation.")
            continue
        df.sort_values("frame_number", inplace=True)
        df['time_sec'] = df['frame_number'] / FRAME_RATE
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        title = base_name.replace("_emotional_analysis", "")
        all_data = [(df, title)]
        total_frames = len(df)
        print(f"For file {csv_file}, total frames: {total_frames}")

        # Set up segmentation for animation
        segment_length_frames = total_frames // NUM_SEGMENTS
        segments = []
        current_start_frame = 0

        for i in range(NUM_SEGMENTS):
            seg_index = i + 1
            seg_end_frame = current_start_frame + segment_length_frames
            if seg_index == NUM_SEGMENTS:  # Last segment
                seg_end_frame = total_frames
            segments.append((seg_index, current_start_frame, seg_end_frame, total_frames, all_data))
            current_start_frame = seg_end_frame

        print("\nSegments:")
        for seg_tuple in segments:
            seg_idx, s_start, s_end, _, _ = seg_tuple
            print(f"Segment {seg_idx}: Frames {s_start}..{s_end}")

        print(f"Creating animation for {csv_file} in {NUM_SEGMENTS} segments.")
        start_processing = time.time()

        pool = multiprocessing.Pool(processes=POOL_SIZE)
        results = pool.starmap(produce_segment, [(seg_index, s_start, s_end, total_frames, all_data)
                                                 for seg_index, s_start, s_end, _, _ in segments])
        pool.close()
        pool.join()

        success_count = sum(results)
        failed_segments = [i + 1 for i, success in enumerate(results) if not success]
        total_time = time.time() - start_processing
        print(f"\nAnimation for {csv_file} processed in {total_time:.1f} seconds, success {success_count}/{NUM_SEGMENTS}")

        # FFmpeg concatenation
        concat_file_path = os.path.join(ANIMATIONS_DIR, f"{base_name}_concat_list.txt")
        with open(concat_file_path, "w", encoding="utf-8") as f:
            for i in range(1, NUM_SEGMENTS + 1):
                seg_path = os.path.join(ANIMATIONS_DIR, f"segment_{i}.mp4")
                f.write(f"file '{seg_path}'\n")

        final_merged_path = os.path.join(ANIMATIONS_DIR, f"{base_name}_animation.mp4")
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file_path,
            "-c:v", "libx264",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            final_merged_path
        ]

        try:
            print("Starting FFmpeg concatenation...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"Final animation saved to: {final_merged_path}")
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg error: {e}")
        except FileNotFoundError:
            print("FFmpeg could not find any files to combine.")

        print("Animation creation complete for this file.\n")

        # Stop the global timer for the visualization process
    overall_end = time.time()
    overall_duration = overall_end - overall_start
    print(
        f"Total visualization time: {overall_duration:.2f} seconds "
        f"(started at {datetime.fromtimestamp(overall_start).strftime('%Y-%m-%d %H:%M:%S')}, "
        f"finished at {datetime.fromtimestamp(overall_end).strftime('%Y-%m-%d %H:%M:%S')})."
    )
        

if __name__ == "__main__":
    run_visualisation()