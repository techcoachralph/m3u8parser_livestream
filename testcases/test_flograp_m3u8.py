from pprint import pprint

import requests
import m3u8
import ssl

# m3u8_response = requests.get('https://d17cyqyz9yhmep.cloudfront.net/streams/94032/playlist_1679767642220_1679768011421.m3u8')
# print(f"Status code: {m3u8_response.status_code}")
# assert m3u8_response.status_code == 200, f"Actual status code {m3u8_response.status_code}"
#
# print("M3U8 content")
# # print(m3u8_response.text)
#
# ralph_gets_destroyed_in_bjj_playlist_local = m3u8.loads(m3u8_response.text)
# # print(f"Is this file variant?????? {ralph_gets_destroyed_in_bjj_playlist_local.is_variant}")
# # print(f"What playlists are in this variant manifest???\n {ralph_gets_destroyed_in_bjj_playlist_local.playlists}")
# for quality_manifest in ralph_gets_destroyed_in_bjj_playlist_local.playlists:
#     print("get path from uri?")
#     print(quality_manifest.base_uri)
#     print("Stream info")
#     print(quality_manifest.stream_info)
# # print(ralph_gets_destroyed_in_bjj_playlist_local.segments)
# # print(ralph_gets_destroyed_in_bjj_playlist_local.target_duration)

'''
for next week:
use selenium wire to navigate to the site to get the m3u8 uri
set the m3u8 uri as a variable
pass the m3u8 uri to the m3u8 parser
tests should still validate as it currently does
'''

ralph_gets_destroyed_in_bjj_playlist = m3u8.load('http://d17cyqyz9yhmep.cloudfront.net/streams/94032/playlist_1679767642220_1679768011421.m3u8')
print("Variant Manifest URI:")
print('http://d17cyqyz9yhmep.cloudfront.net/streams/94032/playlist_1679767642220_1679768011421.m3u8')
# print("Playlists")
# pprint(ralph_gets_destroyed_in_bjj_playlist.data)
# print("--------------")
# print("Variant Manifest Data:")
# pprint(ralph_gets_destroyed_in_bjj_playlist)
# print("--------------")
assert ralph_gets_destroyed_in_bjj_playlist.is_variant is True,\
    "Expected: Variant Manifest is True\n" \
    f"Actual: Variant Manifest is {ralph_gets_destroyed_in_bjj_playlist.is_variant}"

resolutions_for_manifests = ["1280x720", "960x540", "800x450", "640x360", "480x270"]

for index, ralph_gets_destroyed_quality_manifest in enumerate(ralph_gets_destroyed_in_bjj_playlist.playlists):
    assert resolutions_for_manifests[index] == \
           f"{ralph_gets_destroyed_quality_manifest.stream_info.resolution[0]}x" \
           f"{ralph_gets_destroyed_quality_manifest.stream_info.resolution[1]}",\
           f"Expected Resolution: {resolutions_for_manifests[index]}\n" \
           f"Actual Resolution: {ralph_gets_destroyed_quality_manifest.stream_info.resolution[0]}" \
           f"x{ralph_gets_destroyed_quality_manifest.stream_info.resolution[1]}"
    playlist = m3u8.load(ralph_gets_destroyed_quality_manifest.absolute_uri)
    print("Quality Manifest Resolution:")
    print(ralph_gets_destroyed_quality_manifest.stream_info.resolution)
    print("Quality Manifest URI:")
    print(ralph_gets_destroyed_quality_manifest.absolute_uri)
    print("TS Segment:")
    for ts_segment in playlist.segments.uri:
        full_ts_segment_path = playlist.base_uri + ts_segment
        print(full_ts_segment_path)
        ts_response = requests.get(full_ts_segment_path)
        assert ts_response.status_code == 200, \
            "Expected: Status code 200\n" \
            f"Actual: Status Code {ts_response.status_code}\n" \
            f"Failed on Segment: {full_ts_segment_path}"

        assert ts_response.headers["Content-Type"] == "video/MP2T", \
            "Expected: Content-Type to be video/MP2T\n" \
            f"Actual: Content-Type is {ts_response.headers['Content-Type']}"\
            f"Failed on Segment: {full_ts_segment_path}"

        assert ts_response.headers['X-Cache'] == "Hit from cloudfront", \
            "Expected: X-Cache to be Hit from cloudfront\n" \
            f"Actual: X-Cache was {ts_response.headers['X-Cache']}"\
            f"Failed on Segment: {full_ts_segment_path}"
    print("--------------")
# print("--------------")



