import argparse
import asyncio
import json
import os
import shutil
import PIL.Image

if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from edge_tts import Communicate
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips

from renderers.slide_renderer import render_bullet_slide
from renderers.code_renderer import render_code_slide
from renderers.diagram_renderer import render_diagram

DEFAULT_THEME = {
    "bg_color": [20, 24, 33],
    "card_color": [30, 36, 50],
    "accent_color": [56, 189, 248],
    "alert_color": [239, 68, 68],
    "text_main": [240, 244, 250],
    "text_muted": [156, 163, 175],
}


async def generate_tts(text, voice, output_audio_path):
    communicate = Communicate(text, voice)
    await communicate.save(output_audio_path)


def render_visual_for_scene(scene, output_img_path, theme):
    visual = scene["visual"]
    v_type = visual.get("type")

    if v_type == "bullets":
        render_bullet_slide(visual, output_img_path, theme)
    elif v_type == "code":
        render_code_slide(visual, output_img_path, theme)
    elif v_type == "diagram":
        render_diagram(visual, output_img_path, theme)
    elif v_type == "custom_image":
        shutil.copy(visual["path"], output_img_path)
    else:
        raise ValueError(f"Unknown visual type: {v_type}")


def process_scene(scene, idx, work_dir, voice, theme):
    scene_id = scene.get("id", f"scene_{idx:02d}")
    audio_path = os.path.join(work_dir, f"{scene_id}.mp3")
    image_path = os.path.join(work_dir, f"{scene_id}.png")

    print(f"[{idx}] Generating visual: {scene_id} ({scene['visual']['type']})")
    render_visual_for_scene(scene, image_path, theme)

    print(f"[{idx}] Synthesizing speech narration...")
    asyncio.run(generate_tts(scene["narration"], voice, audio_path))

    audio_clip = AudioFileClip(audio_path)
    # 350ms breathing pause between sections for smooth delivery
    duration = audio_clip.duration + 0.35

    video_clip = (
        ImageClip(image_path)
        .set_duration(duration)
        .set_audio(audio_clip)
        .resize((1920, 1080))
    )
    return video_clip, audio_clip


def build_video_from_spec(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    video_title = data.get("title", "output_video")
    out_dir = data.get("output_dir", "output")
    os.makedirs(out_dir, exist_ok=True)

    output_filename = os.path.join(
        out_dir, data.get("output_file", f"{video_title.lower().replace(' ', '_')}.mp4")
    )
    voice = data.get("voice", "en-US-ChristopherNeural")
    theme = data.get("theme", DEFAULT_THEME)
    scenes = data.get("scenes", [])

    work_dir = os.path.join("temp_build", video_title.lower().replace(" ", "_"))
    os.makedirs(work_dir, exist_ok=True)

    video_clips = []
    loaded_audio_clips = []

    print(f"\n============================================================")
    print(f"  EXECUTING ENGINE: {video_title}")
    print(f"  Total Chapters/Scenes: {len(scenes)}")
    print(f"  Voice Model: {voice}")
    print(f"============================================================\n")

    final_video = None
    try:
        for idx, scene in enumerate(scenes, start=1):
            clip, a_clip = process_scene(scene, idx, work_dir, voice, theme)
            video_clips.append(clip)
            loaded_audio_clips.append(a_clip)

        print("\nStitching video sequence...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        print(f"Compiling hardware-optimized MP4 -> {output_filename}")
        temp_audio_path = os.path.join(work_dir, "temp_audio.m4a")
        # Optimized for i5-10210U: 4 threads, preset 'faster' prevents RAM paging
        final_video.write_videofile(
            output_filename,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="faster",
            threads=4,
            bitrate="8000k",
            temp_audiofile=temp_audio_path,
            remove_temp=False,
        )
        print(f"\n[COMPLETE] Video generated successfully: {output_filename}\n")

    finally:
        # Proper file descriptor release on Windows
        if final_video is not None:
            try:
                final_video.close()
            except Exception:
                pass
        for a in loaded_audio_clips:
            try:
                a.close()
            except Exception:
                pass
        for v in video_clips:
            try:
                v.close()
            except Exception:
                pass

        print("Cleaning up temporary scratchpad buffers...")
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Headless Video Engine")
    parser.add_argument(
        "--script", required=True, help="Path to video script JSON file"
    )
    args = parser.parse_args()

    build_video_from_spec(args.script)
