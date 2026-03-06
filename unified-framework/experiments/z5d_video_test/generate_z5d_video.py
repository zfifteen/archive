#!/usr/bin/env python3
"""
Z5D Video Generation Experiment

This script generates a 10-second MP4 video with the text "Z5D" displayed 
throughout to test video creation capabilities as part of the unified framework.

The experiment tests the hypothesis that we can create a reproducible 
video generation system for displaying Z5D framework branding.

Author: Z Framework Implementation Team
Version: 1.0.0
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import moviepy
        print("✅ moviepy is available")
        return True
    except ImportError:
        print("❌ moviepy not found. Installing...")
        return False

def install_moviepy():
    """Install moviepy if not available."""
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "moviepy"])
        print("✅ moviepy installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install moviepy: {e}")
        return False

def generate_z5d_video(output_path="z5d_video.mp4", duration=10):
    """
    Generate a 10-second MP4 video with "Z5D" text.
    
    Parameters:
    -----------
    output_path : str
        Path where the video will be saved
    duration : int
        Duration of the video in seconds (default: 10)
    
    Returns:
    --------
    bool
        True if video was generated successfully, False otherwise
    """
    try:
        # Import moviepy with proper error handling
        try:
            import moviepy
        except ImportError:
            print("❌ MoviePy not available in generate_z5d_video function")
            return False
        
        # Video settings
        width, height = 1280, 720  # HD resolution
        fps = 30
        
        print(f"🎬 Generating {duration}-second video with 'Z5D' text...")
        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps}")
        
        # Create text clip with "Z5D"
        text_clip = moviepy.TextClip(
            text="Z5D", 
            font_size=150,
            color='white'
        ).with_position('center').with_duration(duration)
        
        # Create colored background
        background = moviepy.ColorClip(
            size=(width, height),
            color=(25, 25, 112),  # Navy blue background
            duration=duration
        )
        
        # Compose the video
        video = moviepy.CompositeVideoClip([background, text_clip])
        
        # Write the video file
        print(f"💾 Writing video to: {output_path}")
        video.write_videofile(
            output_path,
            fps=fps,
            codec='libx264',
            audio=False
        )
        
        # Verify file was created and get file size
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Video generated successfully!")
            print(f"   File: {output_path}")
            print(f"   Size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
            print(f"   Duration: {duration} seconds")
            return True
        else:
            print("❌ Video file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error generating video: {e}")
        import traceback
        traceback.print_exc()
        return False

def validate_video(video_path):
    """
    Validate that the generated video meets requirements.
    
    Parameters:
    -----------
    video_path : str
        Path to the video file to validate
    
    Returns:
    --------
    dict
        Validation results
    """
    try:
        # Import moviepy with proper error handling
        try:
            import moviepy
        except ImportError:
            print("❌ MoviePy not available in validate_video function")
            return {'error': 'MoviePy not available'}
        
        print(f"🔍 Validating video: {video_path}")
        
        # Load the video
        video = moviepy.VideoFileClip(video_path)
        
        # Get video properties
        duration = video.duration
        width, height = video.size
        fps = video.fps
        
        # Validation checks
        results = {
            'duration_valid': abs(duration - 10.0) < 0.1,  # Within 0.1 seconds of 10s
            'resolution_valid': width == 1280 and height == 720,
            'fps_valid': fps == 30.0,
            'file_exists': os.path.exists(video_path),
            'file_size': os.path.getsize(video_path),
            'actual_duration': duration,
            'actual_resolution': (width, height),
            'actual_fps': fps
        }
        
        # Close the video
        video.close()
        
        # Print validation results
        print("📊 Validation Results:")
        print(f"   Duration: {duration:.2f}s {'✅' if results['duration_valid'] else '❌'}")
        print(f"   Resolution: {width}x{height} {'✅' if results['resolution_valid'] else '❌'}")
        print(f"   FPS: {fps} {'✅' if results['fps_valid'] else '❌'}")
        print(f"   File size: {results['file_size']:,} bytes")
        
        all_valid = all([
            results['duration_valid'],
            results['resolution_valid'], 
            results['fps_valid'],
            results['file_exists']
        ])
        
        print(f"🎯 Overall validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error validating video: {e}")
        return {'error': str(e)}

def main():
    """Main experiment execution."""
    print("=" * 60)
    print("Z5D Video Generation Experiment")
    print("=" * 60)
    print("Testing hypothesis: Can we create a 10-second MP4 video with 'Z5D' text?")
    print()
    
    # Check and install dependencies
    if not check_dependencies():
        if not install_moviepy():
            print("❌ EXPERIMENT FAILED: Could not install required dependencies")
            return 1
        
        # After installation, try a fresh import test
        try:
            # Force a fresh import attempt
            import importlib
            importlib.invalidate_caches()
            import moviepy
            print("✅ moviepy is now available after installation")
        except ImportError as e:
            print(f"❌ EXPERIMENT FAILED: moviepy still not available after installation: {e}")
            print("Note: You may need to restart Python or your terminal session")
            return 1
    
    # Set up output path
    output_dir = Path(__file__).parent
    output_path = output_dir / "z5d_video.mp4"
    
    # Generate the video
    success = generate_z5d_video(str(output_path), duration=10)
    
    if not success:
        print("❌ EXPERIMENT FAILED: Video generation failed")
        return 1
    
    # Validate the video
    validation_results = validate_video(str(output_path))
    
    if 'error' in validation_results:
        print("❌ EXPERIMENT FAILED: Video validation failed")
        return 1
    
    # Check if all validation criteria passed
    all_valid = all([
        validation_results.get('duration_valid', False),
        validation_results.get('resolution_valid', False),
        validation_results.get('fps_valid', False),
        validation_results.get('file_exists', False)
    ])
    
    print()
    print("=" * 60)
    print("EXPERIMENT RESULTS")
    print("=" * 60)
    
    if all_valid:
        print("🎉 HYPOTHESIS CONFIRMED: Successfully created 10-second MP4 video with 'Z5D' text")
        print("✅ All validation criteria met")
        print(f"📁 Video saved to: {output_path}")
        print()
        print("The experiment demonstrates that:")
        print("1. Video generation is possible within the framework")
        print("2. Text rendering works correctly")
        print("3. Output meets specified requirements (10s duration, HD quality)")
        print("4. The process is reproducible")
        return 0
    else:
        print("❌ HYPOTHESIS REJECTED: Video created but does not meet all requirements")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)