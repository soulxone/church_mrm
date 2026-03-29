import frappe
import json
from urllib.request import urlopen, Request
from urllib.parse import quote


@frappe.whitelist()
def fetch_oembed(youtube_url):
    """Fetch video metadata from YouTube's oEmbed endpoint (no API key required).

    Returns: dict with title, thumbnail_url, video_id
    """
    if not youtube_url:
        return {}

    oembed_url = "https://www.youtube.com/oembed?url={}&format=json".format(
        quote(youtube_url, safe="")
    )

    try:
        req = Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
        response = urlopen(req, timeout=10)
        data = json.loads(response.read().decode("utf-8"))
    except Exception:
        frappe.log_error("YouTube oEmbed fetch failed for: " + youtube_url)
        return {}

    # Extract video_id using the doctype's static method
    from church_mrm.church_mrm.doctype.church_video.church_video import ChurchVideo
    video_id = ChurchVideo.extract_video_id(youtube_url)

    # Use maxresdefault thumbnail (1280x720) instead of oEmbed's smaller one
    thumbnail_url = data.get("thumbnail_url", "")
    if video_id:
        thumbnail_url = "https://img.youtube.com/vi/{}/maxresdefault.jpg".format(video_id)

    return {
        "title": data.get("title", ""),
        "thumbnail_url": thumbnail_url,
        "video_id": video_id or "",
    }
