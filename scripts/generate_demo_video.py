"""
VeriMinion Automated Demo Video Generator
----------------------------------------
Drives the 3-Panel Tactical Command Center UI at http://localhost:8000 using Playwright,
synthesizes studio-grade English voiceover using edge-tts, and stitches them with FFmpeg
into a high-resolution, institutional-grade walkthrough MP4 at demo/veriminion_walkthrough.mp4.
"""

import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
import imageio_ffmpeg
from playwright.sync_api import sync_playwright

# Setup Paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEMO_DIR = REPO_ROOT / "demo"
TEMP_DIR = DEMO_DIR / "temp"
OUTPUT_VIDEO = DEMO_DIR / "veriminion_walkthrough.mp4"

DEMO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Scene Scripts for Edge-TTS Voiceover
SCENE_SCRIPTS = [
    {
        "scene_id": "scene1_overview",
        "title": "Scene 1: Tactical Command Center & SDK Overview",
        "voiceover": (
            "Welcome to VeriMinion, an institutional-grade decentralized inference validator and Byzantine routing engine "
            "built for Cortensor Hackathon 5. Fully powered by all 10 core building blocks of the OpenMinion 0.1 SDK, "
            "VeriMinion solves decentralized AI's greatest vulnerabilities: model spoofing, silent hallucinations, "
            "and adversarial drift across untrusted inference nodes."
        ),
        "post_padding": 1.0
    },
    {
        "scene_id": "scene2_delegation",
        "title": "Scene 2: Mission Intake & Multi-Minion DAG Delegation",
        "voiceover": (
            "Operators can select from four one-click verification presets. Here, we select Preset 1: Cryptographic Smart Contract Audit "
            "and launch the verification mission. Instantly, the Lead Orchestrator Minion decomposes the mission DAG "
            "and dispatches parallel inference workloads across three distinct Cortensor node profiles: Node-Alpha, Node-Beta, and Node-Gamma."
        ),
        "post_padding": 1.2
    },
    {
        "scene_id": "scene3_consensus",
        "title": "Scene 3: Deterministic Tool Verification & Consensus Arena",
        "voiceover": (
            "In the Consensus Arena, the independent Auditor Minion executes real deterministic verification tools—leveraging "
            "Python AST syntax analysis and SymPy symbolic mathematical proofs, rather than unreliable LLM-as-a-judge. "
            "While Node-Alpha and Node-Beta pass Checks-Effects-Interactions standards, Node-Gamma is flagged with Byzantine drift "
            "for unauthorized operating system calls and reentrancy state mutations."
        ),
        "post_padding": 1.2
    },
    {
        "scene_id": "scene4_airlock",
        "title": "Scene 4: Cryptographic Permission Airlock & Ledger Mutation",
        "voiceover": (
            "Adversarial drift immediately engages the Cryptographic Permission Airlock. High-impact operations cannot mutate "
            "decentralized routing tables without human consent. With an immutable SHA-256 mutation hash, the operator approves quarantine. "
            "The Node Reputation Ledger instantly mutates Node-Gamma's status to Quarantined and permanently logs the failure signature "
            "into Semantic Dead-End Memory."
        ),
        "post_padding": 1.2
    },
    {
        "scene_id": "scene5_xray",
        "title": "Scene 5: OpenMinion 0.1 X-Ray Studio & Submission Export",
        "voiceover": (
            "On the right, the OpenMinion 0.1 X-Ray Studio provides complete observability across all 10 building blocks in real time—"
            "capturing execution timings, invocation metrics, and SDK hooks. Finally, the operator exports the complete hackathon QA "
            "submission bundle, containing live memory snapshots and verification evidence."
        ),
        "post_padding": 1.0
    },
    {
        "scene_id": "scene6_outro",
        "title": "Scene 6: Outro & Hackathon Mission Alignment",
        "voiceover": (
            "VeriMinion: Verifiable Proof-of-Cognition, Byzantine fault tolerance, and institutional multi-agent orchestration "
            "for the Cortensor decentralized intelligence network."
        ),
        "post_padding": 2.0
    }
]


def probe_audio_duration(file_path: Path) -> float:
    """Uses FFmpeg to extract exact audio duration in seconds."""
    cmd = [FFMPEG_EXE, "-i", str(file_path)]
    p = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", p.stderr)
    if m:
        h, mn, s = m.groups()
        return int(h) * 3600 + int(mn) * 60 + float(s)
    return 10.0


async def generate_voiceover_tracks() -> list[dict]:
    """Generates studio-grade voiceover tracks using Edge-TTS."""
    import edge_tts

    print("\n[1/4] Synthesizing Studio Voiceover Tracks with Edge-TTS...")
    voice = "en-US-ChristopherNeural"  # Professional, authoritative voice
    tracks = []

    for idx, sc in enumerate(SCENE_SCRIPTS):
        audio_path = TEMP_DIR / f"{sc['scene_id']}.mp3"
        silence_path = TEMP_DIR / f"{sc['scene_id']}_silence.mp3"
        print(f"  -> Synthesizing {sc['title']}...")
        comm = edge_tts.Communicate(sc["voiceover"], voice, rate="+2%", pitch="+0Hz")
        await comm.save(str(audio_path))

        # Generate exact silence padding with FFmpeg
        pad_sec = sc["post_padding"]
        subprocess.run([
            FFMPEG_EXE, "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(pad_sec),
            "-acodec", "libmp3lame",
            str(silence_path)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        dur = probe_audio_duration(audio_path)
        total_scene_dur = dur + pad_sec
        print(f"     Duration: {dur:.2f}s (+ {pad_sec}s pause = {total_scene_dur:.2f}s)")

        tracks.append({
            **sc,
            "audio_path": audio_path,
            "silence_path": silence_path,
            "speech_duration": dur,
            "total_duration": total_scene_dur
        })

    # Assemble master concatenated audio track with FFmpeg
    concat_list_file = TEMP_DIR / "audio_concat.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for t in tracks:
            f.write(f"file '{t['audio_path'].as_posix()}'\n")
            f.write(f"file '{t['silence_path'].as_posix()}'\n")

    master_audio_path = TEMP_DIR / "master_audio.mp3"
    concat_cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(master_audio_path)
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    master_dur = probe_audio_duration(master_audio_path)
    print(f"  -> Master Audio Track Created: {master_dur:.2f}s total duration.")

    return tracks


def ensure_server_running():
    """Checks if http://127.0.0.1:8000 is running; if not, launches it in background."""
    import urllib.request
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=2) as resp:
            if resp.status == 200:
                print("  -> VeriMinion server is already active on http://127.0.0.1:8000")
                return None
    except Exception:
        pass

    print("  -> Launching VeriMinion FastAPI server in background...")
    proc = subprocess.Popen(
        [sys.executable, str(REPO_ROOT / "run.py")],
        cwd=str(REPO_ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    for _ in range(20):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=1) as resp:
                if resp.status == 200:
                    print("  -> Server successfully launched and verified online!")
                    return proc
        except Exception:
            pass
    raise RuntimeError("Failed to verify VeriMinion server on http://127.0.0.1:8000")


def record_ui_walkthrough(tracks: list[dict]) -> Path:
    """Drives the UI at http://localhost:8000 through the 6 scenes while capturing screen."""
    print("\n[2/4] Automating 3-Panel Tactical Command Center UI with Playwright...")
    video_capture_dir = TEMP_DIR / "raw_video"
    if video_capture_dir.exists():
        shutil.rmtree(video_capture_dir)
    video_capture_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(video_capture_dir),
            record_video_size={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        print("  -> Navigating to http://127.0.0.1:8000...")
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Inject Virtual Tactical Glowing Cursor and Highlighter into DOM
        page.evaluate("""() => {
            const cursor = document.createElement('div');
            cursor.id = 'tactical-cursor';
            cursor.style.position = 'fixed';
            cursor.style.width = '26px';
            cursor.style.height = '26px';
            cursor.style.borderRadius = '50%';
            cursor.style.border = '2px solid #06b6d4';
            cursor.style.backgroundColor = 'rgba(6, 182, 212, 0.45)';
            cursor.style.boxShadow = '0 0 16px rgba(6, 182, 212, 0.9)';
            cursor.style.pointerEvents = 'none';
            cursor.style.zIndex = '9999999';
            cursor.style.transition = 'all 0.5s cubic-bezier(0.25, 1, 0.5, 1)';
            cursor.style.transform = 'translate(960px, 540px)';
            document.body.appendChild(cursor);

            window.moveCursorTo = (x, y) => {
                cursor.style.transform = `translate(${x - 13}px, ${y - 13}px)`;
            };

            window.clickCursor = () => {
                cursor.style.transform += ' scale(0.7)';
                setTimeout(() => {
                    cursor.style.transform = cursor.style.transform.replace(' scale(0.7)', '');
                }, 200);
            };
        }""")

        def smooth_move(x, y, click=False):
            page.evaluate(f"window.moveCursorTo({x}, {y})")
            page.wait_for_timeout(600)
            if click:
                page.evaluate("window.clickCursor()")
                page.mouse.click(x, y)
                page.wait_for_timeout(300)

        # =====================================================================
        # SCENE 1: Overview of Tactical Command Center & Status Indicators
        # =====================================================================
        s1 = tracks[0]
        print(f"  -> Recording {s1['title']} ({s1['total_duration']:.2f}s)...")
        start_time = time.time()
        
        # Hover brand & status badges
        smooth_move(180, 25)
        page.wait_for_timeout(1500)
        smooth_move(340, 25)
        page.wait_for_timeout(1500)
        smooth_move(1750, 40)
        page.wait_for_timeout(2000)

        # Wait remaining duration of scene 1
        elapsed = time.time() - start_time
        rem = max(0.5, s1["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 2: Selecting Preset P1 and Triggering "LAUNCH AUDIT"
        # =====================================================================
        s2 = tracks[1]
        print(f"  -> Recording {s2['title']} ({s2['total_duration']:.2f}s)...")
        start_time = time.time()

        # Move to Preset 1 and click
        preset1_btn = page.locator("button:has-text('P1: AST & REENTRANCY')").first
        if preset1_btn.is_visible():
            box = preset1_btn.bounding_box()
            smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
            page.wait_for_timeout(1000)

        # Move to "LAUNCH AUDIT" button and click
        launch_btn = page.locator("button:has-text('LAUNCH AUDIT')").first
        if launch_btn.is_visible():
            box = launch_btn.bounding_box()
            smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
            print("     -> Audit Launched! Observing DAG & A2A Stream...")

        # Watch DAG tasks update on left panel
        smooth_move(160, 160)
        page.wait_for_timeout(2500)
        smooth_move(160, 240)
        page.wait_for_timeout(2500)

        elapsed = time.time() - start_time
        rem = max(0.5, s2["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 3: Highlighting Consensus Arena & Deterministic Verification
        # =====================================================================
        s3 = tracks[2]
        print(f"  -> Recording {s3['title']} ({s3['total_duration']:.2f}s)...")
        start_time = time.time()

        # Focus on Node-Alpha (Verified)
        smooth_move(500, 240)
        page.wait_for_timeout(2500)

        # Focus on Node-Beta (Verified)
        smooth_move(960, 240)
        page.wait_for_timeout(2500)

        # Focus on Node-Gamma (Byzantine Drift Detected)
        smooth_move(1420, 240)
        page.wait_for_timeout(3500)

        # Move to live terminal stream below
        smooth_move(960, 750)
        page.wait_for_timeout(2000)

        elapsed = time.time() - start_time
        rem = max(0.5, s3["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 4: Permission Airlock Banner & Operator Quarantine Approval
        # =====================================================================
        s4 = tracks[3]
        print(f"  -> Recording {s4['title']} ({s4['total_duration']:.2f}s)...")
        start_time = time.time()

        # Focus on Permission Airlock Banner
        airlock_banner = page.locator("text=CRITICAL: PERMISSION AIRLOCK ENGAGED").first
        if airlock_banner.is_visible():
            box = airlock_banner.bounding_box()
            smooth_move(box["x"] + 150, box["y"] + 20)
            page.wait_for_timeout(2000)

        # Enter operator note
        note_input = page.locator("input[placeholder='Optional operator note...']").first
        if note_input.is_visible():
            box = note_input.bounding_box()
            smooth_move(box["x"] + 50, box["y"] + box["height"]/2, click=True)
            note_input.fill("Quarantine confirmed: Unsafe OS import and reentrancy state mutation.")
            page.wait_for_timeout(1000)

        # Click APPROVE QUARANTINE button
        approve_btn = page.locator("button:has-text('APPROVE QUARANTINE')").first
        if approve_btn.is_visible():
            box = approve_btn.bounding_box()
            smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
            print("     -> Quarantine Approved! Verifying Node Reputation update...")
            page.wait_for_timeout(1500)

        # Highlight Left Panel Node Reputation Ledger mutating to QUARANTINED
        smooth_move(160, 520)
        page.wait_for_timeout(3000)

        elapsed = time.time() - start_time
        rem = max(0.5, s4["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 5: OpenMinion 0.1 X-Ray Studio & QA Export Bundle
        # =====================================================================
        s5 = tracks[4]
        print(f"  -> Recording {s5['title']} ({s5['total_duration']:.2f}s)...")
        start_time = time.time()

        # Hover over 10-card X-Ray Studio on right panel
        smooth_move(1750, 150)
        page.wait_for_timeout(1500)
        smooth_move(1750, 270)
        page.wait_for_timeout(1500)

        # Click Card 3 (Tools) to inspect Telemetry Flyout
        tools_card = page.locator("text=3. Tools").first
        if tools_card.is_visible():
            box = tools_card.bounding_box()
            smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
            page.wait_for_timeout(2500)

            # Close inspector
            close_btn = page.locator("button:has-text('Close Inspector')").first
            if close_btn.is_visible():
                box = close_btn.bounding_box()
                smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
                page.wait_for_timeout(1000)

        # Click "Export Bundle" on Top Bar
        export_btn = page.locator("button:has-text('Export Bundle')").first
        if export_btn.is_visible():
            box = export_btn.bounding_box()
            smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
            page.wait_for_timeout(2500)

            # Click Copy Markdown inside modal
            copy_btn = page.locator("button:has-text('Copy Markdown')").first
            if copy_btn.is_visible():
                box = copy_btn.bounding_box()
                smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
                page.wait_for_timeout(1500)

            # Close Modal
            close_x = page.locator("div.fixed button svg").first
            if close_x.is_visible():
                box = close_x.bounding_box()
                smooth_move(box["x"] + box["width"]/2, box["y"] + box["height"]/2, click=True)
                page.wait_for_timeout(1000)

        elapsed = time.time() - start_time
        rem = max(0.5, s5["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        # =====================================================================
        # SCENE 6: Outro & Steady State Overview
        # =====================================================================
        s6 = tracks[5]
        print(f"  -> Recording {s6['title']} ({s6['total_duration']:.2f}s)...")
        start_time = time.time()

        smooth_move(960, 540)
        page.wait_for_timeout(2000)

        elapsed = time.time() - start_time
        rem = max(0.5, s6["total_duration"] - elapsed)
        page.wait_for_timeout(int(rem * 1000))

        print("  -> Closing browser session and flushing video recording...")
        context.close()
        browser.close()

    # Find the written WebM file
    webm_files = list(video_capture_dir.glob("*.webm"))
    if not webm_files:
        raise FileNotFoundError("Playwright did not output any recorded video WebM files!")
    
    raw_video_path = webm_files[0]
    raw_dur = probe_audio_duration(raw_video_path)
    print(f"  -> Raw Video Captured: {raw_video_path.name} ({raw_dur:.2f}s)")
    return raw_video_path


def stitch_final_video(raw_video_path: Path, master_audio_path: Path):
    """Combines high-res recorded video and studio voiceover track with FFmpeg."""
    print("\n[3/4] Stitching Video and Master Audio Track with FFmpeg...")
    print(f"  -> Target Output: {OUTPUT_VIDEO}")

    # FFmpeg command: high-bitrate H.264 video, crisp AAC audio, 60fps, holding last frame if audio is longer
    cmd = [
        FFMPEG_EXE, "-y",
        "-i", str(raw_video_path),
        "-i", str(master_audio_path),
        "-filter_complex", "[0:v]fps=60,tpad=stop_mode=clone:stop_duration=8[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        str(OUTPUT_VIDEO)
    ]

    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        print("FFmpeg error log:\n", p.stderr)
        raise RuntimeError(f"FFmpeg failed with exit code {p.returncode}")

    final_dur = probe_audio_duration(OUTPUT_VIDEO)
    file_size_mb = OUTPUT_VIDEO.stat().st_size / (1024 * 1024)

    print("\n[4/4] Video Generation Complete!")
    print("==================================================================")
    print(f"  File:       {OUTPUT_VIDEO}")
    print(f"  Duration:   {final_dur:.2f} seconds ({final_dur/60:.2f} mins)")
    print(f"  File Size:  {file_size_mb:.2f} MB")
    print(f"  Framerate:  60 fps (1920x1080 Full HD)")
    print(f"  Audio:      Studio AAC 256kbps / Edge-TTS en-US-ChristopherNeural")
    print("==================================================================")


def main():
    print("==================================================================")
    print("  VERIMINION — AUTOMATED DEMO VIDEO GENERATOR")
    print("  Cortensor Hackathon #5 Winner Edition Walkthrough")
    print("==================================================================")

    # 1. Ensure server is running
    server_proc = ensure_server_running()

    try:
        # 2. Synthesize audio
        tracks = asyncio.run(generate_voiceover_tracks())
        master_audio = TEMP_DIR / "master_audio.mp3"

        # 3. Capture UI Walkthrough with Playwright
        raw_video = record_ui_walkthrough(tracks)

        # 4. Stitch with FFmpeg
        stitch_final_video(raw_video, master_audio)

    finally:
        # Cleanup temporary files (keep final video in demo/)
        if TEMP_DIR.exists():
            try:
                shutil.rmtree(TEMP_DIR)
            except Exception:
                pass


if __name__ == "__main__":
    main()
