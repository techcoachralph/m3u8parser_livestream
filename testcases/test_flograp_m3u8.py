import time

import requests
import m3u8
import selenium

# selenium-wire import
from seleniumwire import webdriver
# webdriver manager import
from webdriver_manager.chrome import ChromeDriverManager
# selenium imports
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

'''
for next week:
add a wait for thumbnail to be clickable - due to page load strategy being eager
capture the url of the m3u8 file
have it run through the m3u8 parser
look through the featured video files on the watch page to verify they are functional
'''
# create the new instance of the driver


should_run_locally = False
if should_run_locally is True:
    options = Options()
    options.add_experimental_option("detach", True)
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
        )
else:
    sw_options = {
        'addr': '0.0.0.0',
        'auto_config': False,
        'port': 8091
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=host.docker.internal:8091')
    chrome_options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Remote(
        command_executor="0.0.0.0:4444",
        options=chrome_options,
        seleniumwire_options=sw_options
    )

# driver.scopes = [
#     '.*cloudfront.net/.*/playlist.m3u8',
# ]

driver.implicitly_wait(15)
driver.maximize_window()
# navigate to a video on the Flo Grappling site
driver.get("https://www.flograppling.com")
time.sleep(10)
# for request in driver.requests:
#     if request.response:
#         # set the captured m3u8 file as the manifest uri variable
#         print(
#             request.url,
#             request.response.status_code,
#             request.response.headers['Content-Type']
#         )
# click on watch
driver.find_element(
    By.XPATH,
    "//flo-link[contains(@class,'aux-links-desktop')]"
    "//a[@data-test='flo-link']/button[@class='link-button']/span[.='Watch']").click()
close_cookie_dialog = len(driver.find_elements(By.CSS_SELECTOR, "button.osano-cm-dialog__close"))
if close_cookie_dialog > 0:
    driver.find_element(By.CSS_SELECTOR, "button.osano-cm-dialog__close").click()
time.sleep(10)
# click on a video
# featured_video_thumbnail = WebDriverWait(driver, 20).until(
#     ec.element_to_be_clickable((By.CSS_SELECTOR, "flo-featured-content-card flo-image-thumbnail"))
# )
action = ActionChains(driver)
# action.move_to_element(driver.find_element(By.CSS_SELECTOR, "flo-large-content-card flo-image-thumbnail")).perform()
# time.sleep(5)
# featured_video_thumbnail.click()
featured_video_thumbnail_list = driver.find_elements(By.CSS_SELECTOR, "h4.featured-content-card__title")
try:
    featured_video_thumbnail_list[0].click()
except selenium.common.exceptions.ElementClickInterceptedException:
    print("Click intercepted")
    featured_video_thumbnail_list[0].click()
# driver.find_element(By.CSS_SELECTOR, "h4.featured-content-card__title").click()
# driver.execute_script("arguments[0].click", featured_video_thumbnail)
# use selenium wire to capture the m3u8 file
time.sleep(60)
# for request in driver.requests:
#     if request.response:
#         # set the captured m3u8 file as the manifest uri variable
#         print(
#             request.url,
#             request.response.status_code,
#             request.response.headers['Content-Type']
#         )
#         manifest_uri = request.url


# manifest_uri = 'http://d17cyqyz9yhmep.cloudfront.net/streams/94032/playlist_1679767642220_1679768011421.m3u8'
ralph_gets_destroyed_in_bjj_playlist = m3u8.load(manifest_uri)
print("Variant Manifest URI:")
print(manifest_uri)
assert ralph_gets_destroyed_in_bjj_playlist.is_variant is True,\
    "Expected: Variant Manifest is True\n" \
    f"Actual: Variant Manifest is {ralph_gets_destroyed_in_bjj_playlist.is_variant}"

# resolutions_for_manifests = ["1280x720", "960x540", "800x450", "640x360", "480x270"]

for index, ralph_gets_destroyed_quality_manifest in enumerate(ralph_gets_destroyed_in_bjj_playlist.playlists):
    # assert resolutions_for_manifests[index] == \
    #        f"{ralph_gets_destroyed_quality_manifest.stream_info.resolution[0]}x" \
    #        f"{ralph_gets_destroyed_quality_manifest.stream_info.resolution[1]}",\
    #        f"Expected Resolution: {resolutions_for_manifests[index]}\n" \
    #        f"Actual Resolution: {ralph_gets_destroyed_quality_manifest.stream_info.resolution[0]}" \
    #        f"x{ralph_gets_destroyed_quality_manifest.stream_info.resolution[1]}"

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

        assert ts_response.headers["Content-Type"] == "application/octet-stream", \
            "Expected: Content-Type to be application/octet-stream\n" \
            f"Actual: Content-Type is {ts_response.headers['Content-Type']}"\
            f"Failed on Segment: {full_ts_segment_path}"
        if ts_response.headers['X-Cache'] != "Hit from cloudfront":
            ts_response = requests.get(full_ts_segment_path)
        assert ts_response.headers['X-Cache'] == "Hit from cloudfront", \
            "Expected: X-Cache to be Hit from cloudfront\n" \
            f"Actual: X-Cache was {ts_response.headers['X-Cache']}"\
            f"Failed on Segment: {full_ts_segment_path}"
    print("--------------")
# print("--------------")



