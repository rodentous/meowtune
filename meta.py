# import youtubemusic
import yandexmusic
import os


TARGET_DIR = "downloads"


class Track:
    def __init__(
        self, track_id: str, title: str, artist: str, album: str, duration: str
    ):
        self.track_id: str = track_id
        self.title: str = title
        self.artist: str = artist
        self.album: str = album
        self.duration: str = duration


async def get_track(track_id: str) -> Track:
    t = yandexmusic.get_info(track_id)
    return Track(t[0], t[1], t[2], t[3], t[4])


async def search_tracks(query: str) -> list[Track]:
    results = yandexmusic.search(query)
    tracks = [Track(t[0], t[1], t[2], t[3], t[4]) for t in results]
    return tracks


async def download_track(track_id: str) -> str:
    path = os.path.join(TARGET_DIR, f"{track_id}.mp3")

    if os.path.exists(path):
        return path

    return yandexmusic.download(track_id, path)


async def init():
    await yandexmusic.init()