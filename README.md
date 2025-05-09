# Demonstration of Algorithmic Facial Expression Analysis with DeepFace

Our repository extends but also streamlines the original **DeepFace** package to better meet the needs of organizational researchers working with temporally sensitive video data. Specifically, we introduce support for frame-level synchronization, provide a simplified process designed for multi-video analysis, and include detailed illustrations and include detailed illustrations and annotated scripts that guide users through the full analysis process.


## About DeepFace

**DeepFace** is a versatile open-source library for facial attribute analysis and face recognition. It provides tools to detect faces, analyse emotions, and extract other facial attributes. For more information, visit the official repository: [DeepFace GitHub](https://github.com/serengil/deepface).

### Important Notes:
**DeepFace** builds on the **Facial Action Coding System (FACS)** which defines six basic emotions: joy, sadness, anger, surprise, fear, and disgust. **DeepFace** is configured to detect the following six emotions:
- Happy
- Sad
- Angry
- Surprised
- Disgusted
- Fearful

In addition, **DeepFace** also detects "neutral" emotions. 
In the final visualisations of the example videos, not all emotions may appear. This is because:
1. Some emotions may not be expressed in the video.
2. The default threshold of 80% excludes low-confidence emotions to reduce clutter.


## Overview

This project analyses emotions in any videos using **DeepFace** and generates three types of outputs:
- **Detailed CSV/Excel analysis reports**: Comprehensive data files containing emotion scores for each frame.
- **Emotion distribution plots**: Visual representation of emotions surpassing a defined treshold in each frame across the entire video length.
- **Animated timeline visualisations**: Dynamic timeline showing how emotions evolve throughout the analysed video.

### Key Features

- **Parallel Processing**: Utilizes multiple CPU cores to speed up analysis.
- **Configurable Confidence Thresholds**: Allows users to adjust the minimum confidence level for emotion detection.
- **Support for Multiple Video Formats**: Works with `.mp4`, `.avi`, `.mov`, and `.mkv` files.
- **Combined Analysis Reports**: Generates aggregated CSV and Excel files (spreadsheet data) when analysing multiple videos.

### Contents
- **`data visualisation`**: A folder created in the main project directory where all visual outputs (static image plots and video animations) are saved. The path for this folder is set as `DATA_VISUALISATION_DIR` in the `code_scripts/config.py` file. Both plots and animations are saved directly into this folder.
- **`raw data output files`**: A folder created in the main project directory that stores the detailed results from the emotion analysis. Its path is set as `ANALYSIS_DIR` in the `code_scripts/config.py` file. This folder contains:
    -   **`CSV`**: A subfolder inside `raw data output files` where spreadsheet data is saved in CSV format.
    -   **`Excel`**: A subfolder inside `raw data output files` where spreadsheet data is saved in Excel format.
- **`videos for AFEA demonstration`**: A folder in the main project directory where you should place the video files you want to analyse. Its path is set as `INPUT_VIDEO_DIR` in the `code_scripts/config.py` file.
- **`.gitattributes`**: A configuration file for Git (version control software). Not relevant for running the analysis.
- **`code_scripts/analysis.py`**: The script that performs the emotion analysis on videos from the `videos for AFEA demonstration` folder.
- **`code_scripts/config.py`**: A crucial file where you can change settings like folder paths, analysis sensitivity (thresholds), and performance options.
- **`ffmpeg_installer.py`**: A helper script to install or manage FFmpeg, a necessary tool for creating the animated video visualisations.
- **`install_dependencies.py`**: A script to automatically install all the software packages your computer needs to run this project. It uses the list in `code_scripts/requirements.txt`.
- **`main.py`**: The main script you will run to start the analysis or visualisation.
- **`README.md`**: This file, providing an overview and instructions for the project.
- **`code_scripts/requirements.txt`**: A list of Python software packages required for the project.
- **`code_scripts/visualisation.py`**: The script that creates image plots and video animations from the analysis data found in the `raw data output files/CSV` folder. These visualisations are saved into the `data visualisation` folder.


## Prerequisites

1. **Windows Operating System**:
   - The script is designed to work on Windows 11.

2. **Anaconda 3**:
   - It is highly recommended to install [Anaconda 3](https://www.anaconda.com/products/distribution).
   - Anaconda provides a Python environment with many useful packages pre-installed and simplifies dependency management.

3. **Internet Connection**:
   - The initial installation of the project requires a stable internet connection to download the relevant scripts. 
   - Furthermore the project automatically downloads required resources (e.g., Python libraries or model weights) if they are not found on your system, which also requires a stable internet connection.

4. **Storage Space**:
   - Requires approximately 2–5 GB of free storage, depending on input video size and output files.

5. **Microsoft Visual C++ Redistributable**:
   - Required for FFmpeg to work properly. FFmpeg is used to create the animation of the visualised analysis.
   - Download the latest version from [here](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170&spm=a2ty_o01.29997173.0.0.335ec921D777oq).
	- Properly check which architecture your system has and install the right version: (ARM64, X86, X64).


## Installation Steps

### 1. Install Anaconda 3
- Download and install [Anaconda 3](https://www.anaconda.com/products/distribution) following the instructions for your operating system.
- During installation, ensure that "Anaconda Prompt" is installed to run commands.
- If not directly installed, use "Anaconda Navigator" to install "Anaconda Prompt."

### 2. Download the Project Folder
- Download the entire project folder and place it in a location you remember. Then continue with Step 3.
- Alternatively, you can also clone the GitHub repository directly with Git as described in 2.1 and then step 3 can be skipped.

#### 2.1 Download the Project Folder including exemplary videos through Git
- This might take some time and requires a stable internet connection
- Either now or after initialising Git LFS it is recommended to navigate to a directory where the new folder should be created. For example:
  ```bash
  cd C:\Users\your_username\Documents
  ```
- Ensure Git is installed by entering the following into the Anaconda Prompt: 
  ```bash
  conda install git
  ```
- Install Git LFS
  ```bash
  conda install -c conda-forge git-lfs
  ```
- Initialise Git LFS
  ```bash
  git lfs install
  ```
- Clone the repository
  ```bash
  git clone https://github.com/org-emotion-researcher/DeepFace-Demonstration.git
  ```
- Navigate to the repository and then download all large files
  ```bash
  cd DeepFace-Demonstration
  git lfs pull
  ```
- If this process was successful, you can skip step 3.

### 3. Download or add Relevant Videos
- Download the exemplary videos [here](https://drive.proton.me/urls/T51K7N36PM#6fbJSMs2yPff).
- After downloading, navigate to the `videos for AFEA demonstration` folder within the project and place the exemplary videos or add your own video(s).

### 4. Navigate to the Project Folder
- Open **Anaconda Prompt** as an administrator.
- Change directory (`cd`) to the project folder. For example:
  ```bash
  cd C:\Users\your_username\Documents\Deepface_emotion_analysis
  ```
- To ensure the correct file path, navigate to the folder using **Explorer** (Windows), copy the folder path, and paste it into the terminal.

### 5. Install Dependencies
- Run the following command to install all required dependencies:
  ```bash
  python install_dependencies.py
  ```
- This ensures all necessary libraries, including FFmpeg, are installed properly.


## Conducting the Analysis

### Run the Analysis
- Place your video files (supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`) into the `videos for AFEA demonstration` folder at the project root.
- Use the following command to analyse every `n`-th frame:
  ```bash
  python main.py analysis --frame_step n
  ```
  - Replace `n` with the desired frame skipping rate. For example:
    ```bash
    python main.py analysis --frame_step 1000
    ```
    This analyses every 1000th frame of each video.

- **Tips for Preliminary Testing**:
  - Start with a high `frame_step` value (e.g., 1000) to estimate processing time.
  - Videos typically have 30 frames per second. Multiply the video length (in seconds) by 30 to determine the total number of frames. Then you can estimate the time differences. 
  - Generally, due to long setup times, the increases in time are not linear. An increase from analysing every 1000th frame vs every frame was approximately 100 times longer.

- To analyse every frame, run:
  ```bash
  python main.py analysis
  ```


#### Output of the Analysis:
- One **CSV file** (spreadsheet data) per video, containing the analysis results. These are saved in the `raw data output files/CSV` folder. The main `raw data output files` folder path is defined in `code_scripts/config.py`.
- One **Excel file** (spreadsheet data) per video, containing the same data. These are saved in the `raw data output files/Excel` folder.
- A **combined CSV/Excel file** that aggregates results from all analysed videos, also saved in the respective subfolders within `raw data output files`.


### Run the Visualisation
- After completing the analysis, generate visualisations using:
  ```bash
  python main.py visualisation
  ```
  - Add the optional argument `sheet_name` with the name of the CSV file to visualize. For example:
    ```bash
    python main.py visualisation --sheet entrepreneur1_emotional_analysis.csv
    ```
  - If the name of the sheet has a space in it, put quotes around the name to ensure the correct sheet is analysed. For example:
    ```bash
	python main.py visualisation --sheet "sheet name.csv"
	```

#### Output of the Visualisation:
- **Emotion distribution plot**: A static image showing which emotions were detected above a set confidence level throughout each video. This is saved in the `data visualisation` folder.
- **Animated timeline visualisation**: A video file showing how emotions change over time throughout the analysed video. This is also saved in the `data visualisation` folder.


### Additional Commands
- To perform both analysis and visualisation in one step, run:
  ```bash
  python main.py
  ```


### Customization Options

Most customizations can be done within the `code_scripts/config.py` file. This file acts as a central control panel for the project. The following are the most important variables to adjust:

#### Thresholds
- **`FACE_CONFIDENCE_THRESHOLD` (Default = 0.9)**:
  - This variable sets the confidence threshold for face detection as a **decimal value between 0 and 1**.
  - A higher value ensures only highly confident face detections are processed.
  - Adjust this if you encounter issues with false positives or missed detections.

- **`EMOTION_SCORE_THRESHOLD` (Default = 50)**:
  - This variable determines the threshold for determining when an emotion should be classified as dominant.
  - Value represents **percentage points (0-100)** of confidence in the emotion detection.
  - Emotions that score below this threshold will not be considered dominant.
  - Increase this value to adjust the logic when an emotion is deemed as dominant.

- **`CONFIDENCE_THRESHOLD` (Default = 80)**:
  - This variable defines the minimum confidence level for emotions to be included in the visualization.
  - Value represents **percentage points (0-100)** of confidence in the emotion detection.
  - Emotions rated below this threshold will not appear in the plots or animations.
  - The default value of 80 helps reduce clutter in the visualizations by excluding low-confidence emotions.

#### Plot Dimensions
- **`PLOT_WIDTH` (Default = 19.2)**:
  - Defines the width of the plot in inches.
  - The default value is optimized for a 1920x1080 screen resolution.

- **`PLOT_HEIGHT` (Default = 5.4)**:
  - Defines the height of the plot in inches.
  - Together with `PLOT_WIDTH`, the dimensions are designed to cover half of a 1080p screen, leaving space for side-by-side video comparison.

#### Performance Settings
- **`CPU_CORES` (Default = Auto-detected)**:
  - Automatically detects the number of physical CPU cores on your system.
  - This value serves as the basis for parallel processing. Avoid modifying it unless necessary.

- **`POOL_SIZE` (Default = `(CPU_CORES) // 4`)**:
  - Determines how many processes are executed simultaneously.
  - A higher value speeds up processing but increases CPU and RAM load. Reduce this value if your system struggles with high resource usage.

- **`NUM_SEGMENTS` (Default = `POOL_SIZE * 2`)**:
  - Divides the animation into smaller segments for rendering.
  - Increasing this value reduces memory usage during animation creation but may slightly increase processing time.


## Specifications

- **Analysis Time**: 
  - Three 4.5-minute videos took ~29 minutes to analyse.
  - Each video took ~8–10 minutes to process.

- **Visualisation Time**:
  - Visualizing each dataset took ~16 minutes.
  - Each sheet took ~5–6 minutes to process.

- **Python Version**: 3.11+
- **Hardware Used**:
  - CPU: Ryzen 9 9950X
  - RAM: 64 GB (DDR5, 4800 MT/s)
- GPU acceleration was not utilized.


## Tips for Optimization

- Reduce video quality to decrease processing time.
- Increase the `frame_step` value for faster analysis.


## Troubleshooting
- **FFmpeg Errors**: Ensure Microsoft Visual C++ Redistributable is installed (see Prerequisites).
- **Missing Outputs**: 
    - Check your threshold settings in `code_scripts/config.py` to ensure they are not too strict.
    - Verify that the `raw data output files` and `data visualisation` folders are being created and that the program has permission to write files there.
- **Multiprocessing Failures**: If the analysis crashes or your computer becomes very slow, try reducing the `POOL_SIZE` value in `code_scripts/config.py`. This will use fewer CPU resources.


## **What to Expect While the Code is Running**

Before running any analysis, ensure you have installed all dependencies by executing:

```bash
python install_dependencies.py
```

This section describes the processes displayed in the Anaconda Prompt or terminal when running `python main.py` with no additional arguments. The script provides real-time updates, including progress percentages and completion times. TensorFlow warnings may appear but do not affect functionality.

#### **Analysis Phase**
1. The script will state how many video files have been found and list them.
2. It will then specify which video file processing will begin with.
3. Information about reading the video file will be displayed.
4. The number of detected frames will be stated. This should match the video's duration (in seconds) multiplied by its frame rate (typically 30 FPS).
5. DeepFace will process individual frames, notifying you every time 10% of the video file has been analysed.
6. At the end of each video, a brief recap of the analysed emotions will be provided.
7. If multiple videos are present, steps 2–6 will repeat until all videos are processed.

#### **Visualisation Phase**
8. After completing the analysis, the visualisation process begins.
9. A static plot summarizing the emotions that surpass the confidence threshold is created.
10. The visualisation continues by dividing the frames into segments (default: twice the number of CPU processes).
11. The framework for the animation is initialized, and progress updates are displayed every 10%. Only the most recent segment's progress is shown.
12. Once a segment is complete, a message confirms it has been saved.
13. After all segments are saved, they are automatically combined into a single video file.
14. Steps 10–13 repeat for all available sheets, except the combined one (unless only one sheet is specified).
15. Once all sheets are visualized, the process is complete.

#### **Execution Options**
- If you run only the analysis (`python main.py analysis`), the process stops after step 7.
- If you run only the visualisation (`python main.py visualisation --sheet sheet_name`), the process starts at step 9 and ends at step 15.
````
