# import yt_dlp
from ytmusicapi import YTMusic
import os
import asyncio
from queue import Queue
import subprocess


ytm = YTMusic("browser.json")

async def get_info(videoId: str, info_msg):
    for i in range(3):
        try:
            return ytm.get_song(videoId)
        except:
            await info_msg.edit_text(f"Getting song info failed {i+1}/3")
            pass
    await info_msg.edit_text(f"Getting song info failed")
    return []


async def search(query: str, info_msg):
    for i in range(3):
        try:
            search_results = ytm.search(query, filter="songs", limit=99)
            await info_msg.delete()
            break
        except:
            await info_msg.edit_text(f"Search failed {i+1}/3")
            pass
    else:
        search_results = []

    results = []
    i = 1
    for result in search_results:
        results.append(
            (
                f"{i} | {result.get("title", "Unknown")} | {result.get("artists", "Unknown")[0].get("name", "Unknown")} | {result.get("duration", "Unknown")}",
                result.get("videoId", "HUH???"),
            )
        )
        i += 1
    return results


async def download(track: str, info_msg):
    path = os.path.join("downloads", f"{track}.mp3")
    if os.path.exists(path):
        return path
    
    # Build the command
    cmd = [
        'yt-dlp',
        '--cookies', "cookies.txt",
        '--extract-audio',
        '--audio-format', 'mp3',
        # '--audio-quality', f'{quality}K',
        '--embed-thumbnail',
        '--add-metadata',
        '--output', path,
        '--ignore-errors',
        '--no-overwrites',
        # '--verbose',  # Add verbose for debugging
        f"https://music.youtube.com/watch?v={track}"
    ]

    try:
        # Run the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            check=True    # Raise exception on non-zero exit code
        )
        
        await info_msg.edit_text("Downloaded")
        return path
    
    except Exception as e:
        await info_msg.edit_text(str(e))
        print(f"❌ Unexpected error: {e}")
        return ""
