import os
import time
import re
from collections import Counter

from dotenv import load_dotenv

import regex
import myjdapi
import scraper

load_dotenv()

JD_EMAIL = os.getenv("JD_EMAIL")
JD_PASSWORD = os.getenv("JD_PASSWORD")

if not JD_EMAIL or not JD_PASSWORD:
    raise RuntimeError("Missing JD_EMAIL or JD_PASSWORD in environment.")

jd = myjdapi.Myjdapi()
jd.connect(JD_EMAIL, JD_PASSWORD)
devices = jd.list_devices()
device = jd.get_device(devices[0]["name"])

def reconnect():
    global jd, devices, device
    jd = myjdapi.Myjdapi()
    jd.connect(JD_EMAIL, JD_PASSWORD)
    devices = jd.list_devices()
    device = jd.get_device(devices[0]["name"])

def getName(link):
    numbersList = regex.findNumbers(link["name"])
    return numbersList[0].replace(".", "") + " " + numbersList[1].replace(".", "")


def chooseBestLink(a, b):
    if "mega." in a["url"] and not "mega." in b["url"]:
        return b

    if "mega." in b["url"] and not "mega." in a["url"]:
        return a

    if not "zippyshare" in a["url"] and "zippyshare" in b["url"]:
        return b

    if "bytesTotal" in a.keys() and "bytesTotal" in b.keys() and a["bytesTotal"] < b["bytesTotal"]:
        return b

    return a


VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".m4v"}
EPISODE_NAME_RE = re.compile(r"^(?P<anime_id>\d+)[_ ](?P<episode>\d+)(?:\.(?P<ext>\w+))?$")


def _has_video_extension(value):
    if not value:
        return False
    value = value.split("?", 1)[0].split("#", 1)[0]
    _, ext = os.path.splitext(value)
    return ext.lower() in VIDEO_EXTENSIONS


def _extract_extension(link):
    name = link.get("name", "")
    url = link.get("url", "")
    for value in (name, url):
        if not value:
            continue
        value = value.split("?", 1)[0].split("#", 1)[0]
        _, ext = os.path.splitext(value)
        if ext.lower() in VIDEO_EXTENSIONS:
            return ext.lower()
    return None


def _extract_episode_key(link):
    name = link.get("name", "")
    match = EPISODE_NAME_RE.match(name)
    if not match:
        return None
    return int(match.group("anime_id")), int(match.group("episode"))


def _select_best_links(links):
    candidates = []
    for link in links:
        if link.get("availability") != "ONLINE":
            continue
        if not (_has_video_extension(link.get("name")) or _has_video_extension(link.get("url"))):
            continue
        key = _extract_episode_key(link)
        if not key:
            continue
        anime_id, episode = key
        candidates.append((anime_id, episode, link))

    if not candidates:
        return None, {}

    anime_counts = Counter(anime_id for anime_id, _, _ in candidates)
    selected_anime_id = max(anime_counts, key=anime_counts.get)

    best_per_episode = {}
    for anime_id, episode, link in candidates:
        if anime_id != selected_anime_id:
            continue
        if episode not in best_per_episode:
            best_per_episode[episode] = link
        else:
            best_per_episode[episode] = chooseBestLink(best_per_episode[episode], link)

    return selected_anime_id, best_per_episode


def _normalize_anime_name(anime):
    return anime.replace("-", " ").strip().title()


def _format_episode_name(anime_name, episode, ext, width):
    episode_text = str(episode).zfill(width)
    return f"{anime_name} {episode_text}{ext}"


def _report_selection(anime_id, anime_name, best_per_episode):
    print("\nSelected links:")
    if not best_per_episode:
        return
    width = len(str(max(best_per_episode.keys())))
    for episode in sorted(best_per_episode.keys()):
        link = best_per_episode[episode]
        size = link.get("bytesTotal")
        size_text = f"{size} bytes" if size else "size unknown"
        ext = _extract_extension(link) or ".mp4"
        new_name = _format_episode_name(anime_name, episode, ext, width)
        print(f"  Anime {anime_id} - Episode {episode}: {new_name} ({size_text})")


def downloadLinks(anime_name):
    global device
    links = device.linkgrabber.query_links()
    packages = device.linkgrabber.query_packages()

    anime_id, best_per_episode = _select_best_links(links)
    if not best_per_episode:
        print("No valid video links found in LinkGrabber.")
        return

    _report_selection(anime_id, anime_name, best_per_episode)

    opt = input("\nProceed to add these links to the download list and clean the rest? (y/n): ")
    if opt.lower().strip() != "y":
        print("Canceled.")
        return

    keep_link_ids = {link["uuid"] for link in best_per_episode.values()}
    keep_package_ids = {link["packageUUID"] for link in best_per_episode.values()}

    width = len(str(max(best_per_episode.keys())))
    for episode, link in best_per_episode.items():
        ext = _extract_extension(link) or ".mp4"
        new_name = _format_episode_name(anime_name, episode, ext, width)
        device.linkgrabber.rename_link(link["uuid"], new_name)

    for package_id in keep_package_ids:
        device.linkgrabber.rename_package(package_id, anime_name)

    drop_link_ids = [link["uuid"] for link in links if link["uuid"] not in keep_link_ids]
    drop_package_ids = [pkg["uuid"] for pkg in packages if pkg["uuid"] not in keep_package_ids]

    if drop_link_ids or drop_package_ids:
        device.linkgrabber.remove_links(link_ids=drop_link_ids, package_ids=drop_package_ids)

    device.linkgrabber.move_to_downloadlist(
        link_ids=list(keep_link_ids), package_ids=[])


def cleanLinks():
    global device
    device.linkgrabber.clear_list()


def addLinks(links, package_name=None):
    global device
    for link in links:
        device.linkgrabber.add_links([{
            "autostart": False,
            "links": link,
            "packageName": package_name,
            "extractPassword": None,
            "priority": "DEFAULT",
            "downloadPassword": None,
            "destinationFolder": None,
            "overwritePackagizerRules": False
        }])


def downloadAnime(anime, browser, offset=0, limit=0):
    anime_name = _normalize_anime_name(anime)
    links = scraper.scrapAnime(anime, browser, offset, limit=limit)
    addLinks(links, package_name=anime_name)

    print("\nWaiting for JDownloader LinkGrabber to finish collecting...")
    while device.linkgrabber.is_collecting():
        time.sleep(1)
    reconnect()
    downloadLinks(anime_name)
