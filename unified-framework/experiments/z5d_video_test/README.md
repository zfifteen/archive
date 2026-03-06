# Z5D Video Test Experiment

## Purpose

This experiment tests the hypothesis: **"Can we create a reproducible 10-second MP4 video with the text 'Z5D' displayed throughout?"**

The experiment validates video generation capabilities within the unified framework and demonstrates that video content creation can be systematically tested and validated.

## Hypothesis

**H0 (Null Hypothesis):** It is not possible to create a reproducible 10-second MP4 video with "Z5D" text using Python libraries.

**H1 (Alternative Hypothesis):** It is possible to create a reproducible 10-second MP4 video with "Z5D" text that meets specific quality requirements.

## Success Criteria

The hypothesis will be **confirmed** if all the following criteria are met:

1. ✅ Video duration is exactly 10 seconds (±0.1s tolerance)
2. ✅ Video displays "Z5D" text clearly in the center
3. ✅ Video resolution is 1280x720 (HD)
4. ✅ Video frame rate is 30 FPS
5. ✅ Video file is saved as MP4 format
6. ✅ Process is reproducible across different systems

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Internet connection (for dependency installation)

### Dependencies

The experiment will automatically install the required `moviepy` library if not present. Manual installation can be done with:

```bash
pip install moviepy
```

### System Requirements

- **Operating System:** Linux, macOS, or Windows
- **RAM:** At least 512 MB available
- **Disk Space:** At least 50 MB for video output
- **FFmpeg:** Will be installed automatically by moviepy if needed

## Execution Steps

### 1. Navigate to Experiment Directory

```bash
cd experiments/z5d_video_test
```

### 2. Run the Experiment

```bash
python generate_z5d_video.py
```

### 3. Expected Output

The script will:
1. Check for required dependencies
2. Install moviepy if not present
3. Generate a 10-second video with "Z5D" text
4. Validate the generated video
5. Report success or failure with detailed metrics

### 4. Output Files

- `z5d_video.mp4` - The generated video file
- Console output showing validation results

## Expected Results

### Success Case

```
============================================================
Z5D Video Generation Experiment
============================================================
Testing hypothesis: Can we create a 10-second MP4 video with 'Z5D' text?

✅ moviepy is available
🎬 Generating 10-second video with 'Z5D' text...
   Resolution: 1280x720
   FPS: 30
💾 Writing video to: z5d_video.mp4
✅ Video generated successfully!
   File: z5d_video.mp4
   Size: 234,567 bytes (0.22 MB)
   Duration: 10 seconds
🔍 Validating video: z5d_video.mp4
📊 Validation Results:
   Duration: 10.00s ✅
   Resolution: 1280x720 ✅
   FPS: 30.0 ✅
   File size: 234,567 bytes
🎯 Overall validation: ✅ PASSED

============================================================
EXPERIMENT RESULTS
============================================================
🎉 HYPOTHESIS CONFIRMED: Successfully created 10-second MP4 video with 'Z5D' text
✅ All validation criteria met
📁 Video saved to: z5d_video.mp4

The experiment demonstrates that:
1. Video generation is possible within the framework
2. Text rendering works correctly
3. Output meets specified requirements (10s duration, HD quality)
4. The process is reproducible
```

### Failure Cases

The experiment may fail due to:
- Missing system dependencies (FFmpeg)
- Insufficient disk space
- Network connectivity issues during dependency installation
- System incompatibilities

## Troubleshooting

### Common Issues

1. **"moviepy not found" error:**
   - Ensure internet connection for automatic installation
   - Try manual installation: `pip install moviepy`

2. **FFmpeg errors:**
   - On Ubuntu/Debian: `sudo apt install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from https://ffmpeg.org/

3. **Permission errors:**
   - Ensure write permissions in the experiment directory
   - Run with appropriate user privileges

4. **Memory errors:**
   - Ensure at least 512 MB RAM is available
   - Close other applications if needed

## Reproducibility

This experiment is designed to be fully reproducible across different systems:

- **Deterministic output:** Same video properties every time
- **Automatic dependency management:** Script handles installation
- **Cross-platform compatibility:** Works on Linux, macOS, Windows
- **Version pinning:** Uses specific video parameters for consistency

## Scientific Method Application

This experiment follows the scientific method:

1. **Observation:** Need to create video content for Z5D framework
2. **Question:** Can we reliably generate videos programmatically?
3. **Hypothesis:** Video generation is possible with specific requirements
4. **Experiment:** Automated script with validation
5. **Analysis:** Detailed metrics and validation criteria
6. **Conclusion:** Hypothesis confirmed or rejected based on results

## File Structure

```
experiments/z5d_video_test/
├── README.md                   # This documentation
├── generate_z5d_video.py      # Main experiment script
└── z5d_video.mp4              # Generated video (after execution)
```

## Integration with Unified Framework

This experiment demonstrates:
- Systematic testing methodology
- Automated validation and reporting
- Reproducible research practices
- Clear success/failure criteria
- Integration with the broader Z5D framework ecosystem

## Attribution

- **Created by:** Z Framework Implementation Team
- **Version:** 1.0.0
- **Date:** December 2024
- **Framework:** Unified Z5D Framework

## License

This experiment is part of the unified framework and follows the same licensing terms as the parent project.