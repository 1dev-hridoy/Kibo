"""Camera: camera_photo()."""

import os
import shutil

from agent.config import IS_WINDOWS, IS_MACOS, IS_LINUX
from agent.runner.common import run, _find


def camera_photo(save_path: str = "") -> str:
    """Capture a photo from the first available webcam."""
    from agent.config import PHOTO_PATHS

    if save_path:
        targets = [os.path.expanduser(save_path)]
    else:
        targets = PHOTO_PATHS
    dest = targets[0]
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)

    if IS_LINUX:
        ffmpeg = _find("ffmpeg", "avconv")
        if ffmpeg:
            for dev in ("/dev/video0", "/dev/video1"):
                if os.path.exists(dev):
                    res = run([ffmpeg, "-y", "-f", "v4l2", "-i", dev,
                               "-frames:v", "1", dest], timeout=30)
                    if not res.startswith("Error"):
                        return f"Photo saved to {dest}"
        return "No webcam or capture tool found — cannot take a photo."
    if IS_MACOS:
        if shutil.which("ffmpeg"):
            res = run(["ffmpeg", "-y", "-f", "avfoundation", "-i", "0",
                       "-frames:v", "1", dest], timeout=30)
            if not res.startswith("Error"):
                return f"Photo saved to {dest}"
        return "No webcam access — grant camera permission to the terminal."
    if IS_WINDOWS:
        if shutil.which("ffmpeg"):
            res = run(["ffmpeg", "-y", "-f", "dshow", "-i",
                       "video=Integrated Camera", "-frames:v", "1", dest],
                      timeout=30)
            if not res.startswith("Error"):
                return f"Photo saved to {dest}"
        return "No webcam found — install ffmpeg for camera capture."
    return "No webcam found — camera capture is unavailable on this system."
