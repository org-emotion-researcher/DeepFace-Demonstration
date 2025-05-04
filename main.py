import os
import argparse
import warnings
from analysis import run_analysis
from visualisation import run_visualisation
import config

# Suppress Python deprecation warnings.
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set TensorFlow environment variables.
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # '3' hides INFO, WARNING & ERROR

def main():
    """
    Main function to run the Video Emotion Analysis and Visualisation Tool.
    
    Parses command-line arguments to determine whether to run analysis, 
    visualisation, or both. Also handles optional parameters like frame_step
    for analysis and specific sheet selection for visualisation.
    
    Returns:
        None
    """
    parser = argparse.ArgumentParser(
        description="Video Emotion Analysis and Visualisation Tool"
    )
    
    # Command to choose analysis or visualisation.
    parser.add_argument("command", nargs="?", choices=["analysis", "visualisation"], default=None,
                        help="Specify whether to run 'analysis', 'visualisation', or leave empty to run both.")
    
    # Frame step argument for analysis.
    parser.add_argument("--frame_step", type=int, default=config.FRAME_STEP,
                        help="Analyze every n-th frame (default is as set in config.py).")
    
    # Optional argument for visualisation: specify a particular CSV file (sheet).
    parser.add_argument("--sheet", type=str, default="",
                        help="Optional: specify the analysis CSV file to process (e.g. 'Entrepreneur_emotional_analysis.csv').")
    
    args = parser.parse_args()

    if args.command is None:
        print("No command specified. Running both analysis and visualisation...")
        print(f"Starting analysis with a frame step of every {args.frame_step} frame(s)...")
        run_analysis(frame_step=args.frame_step)
        print("Starting visualisation after analysis...")
        run_visualisation(sheet=args.sheet)
    
    elif args.command == "analysis":
        print(f"Starting analysis with a frame step of every {args.frame_step} frame(s)...")
        run_analysis(frame_step=args.frame_step)
    
    elif args.command == "visualisation":
        print("Starting visualisation...")
        run_visualisation(sheet=args.sheet)

if __name__ == '__main__':
    main()