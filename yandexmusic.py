from yandex_music import ClientAsync


async def init():
	global client
	client = await ClientAsync('y0__xC5kebHBRje-AYgncKrrRQwtdSL-Qc4ejBhgpoMDJL_vusJX2rlFr92Sw').init()


async def get_info(track_id: str) -> list[str]:
	t = await client.tracks(track_id)
	return [
		t.id,
		t.title,
		", ".join([artist.name for artist in t.artists]),
		t.album.title,
		f"{(t.duration_ms//100)//60:02d}:{(t.duration_ms//100)%60:02d}",
	]


async def search(query: str) -> list[list[str]]:
    results = await client.search(query)
    return [
        [
            t.id,
            t.title,
            ", ".join([artist.name for artist in t.artists]),
            t.album.title,
			f"{(t.duration_ms//100)//60:02d}:{(t.duration_ms//100)%60:02d}",
        ]
        for t in results.tracks
    ]


async def download(track_id: str, path: str) -> str:
	t = await client.tracks(track_id)
	await t.download_async(path)
	return path



# async def lyrics(track_id: str) -> str:
# 	pass