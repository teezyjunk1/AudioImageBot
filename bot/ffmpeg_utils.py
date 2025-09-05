import asyncio
import os
import shlex
import uuid
from pathlib import Path

WORKDIR = Path(os.getenv("WORKDIR", "./workdir")).resolve()
WORKDIR.mkdir(parents=True, exist_ok=True)

async def build_video(image_path: Path, audio_path: Path) -> Path:
    """Create a 1920x1080 MP4 with the image centered on black and MP3 audio."""
    out_path = WORKDIR / f"out_{uuid.uuid4().hex}.mp4"

    # Fit image to 1920x1080 without distortion, then pad with black
    # scale: if wider than 16:9 -> width=1920 else height=1080
    vf = (
        "scale='if(gt(a,16/9),1920,-2)':'if(gt(a,16/9),-2,1080)',"
        "setsar=1,"
        "pad=1920:1080:(1920-iw)/2:(1080-ih)/2:black"
    )

    cmd = (
        f"ffmpeg -y -loop 1 -i {shlex.quote(str(image_path))} -i {shlex.quote(str(audio_path))} "
        f"-tune stillimage -c:v libx264 -preset ultrafast -pix_fmt yuv420p -vf {shlex.quote(vf)} "
        f"-c:a aac -b:a 192k -shortest {shlex.quote(str(out_path))}"
    )
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, err = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {err.decode(errors='ignore')[:4000]}")
    return out_path