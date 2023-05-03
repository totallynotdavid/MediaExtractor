import requests
import json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Implement the provided functions
def get_tweet_details(res):
    media_details = res.get("mediaDetails", [])
    result = []
    for media in media_details:
        if media["type"] in ("video", "animated_gif"):
            variants = sorted(
                (x for x in media["video_info"]["variants"] if "bitrate" in x),
                key=lambda x: x["bitrate"],
                reverse=True,
            )
            result.append({"type": "video", "url": variants[0]["url"]})
        else:
            result.append({"type": media["type"], "url": media["media_url_https"]})
    return result

def get_card_details(res):
    card_binding_values = res.get("card", {}).get("binding_values", {})
    if "unified_card" in card_binding_values:
        json_data = json.loads(card_binding_values["unified_card"]["string_value"])
        media_entities = {"mediaDetails": list(json_data["media_entities"].values())}
        return get_tweet_details(media_entities)
    thumbnail_image_original = card_binding_values.get("thumbnail_image_original", {}).get("image_value", {}).get("url")
    if not thumbnail_image_original:
        return []
    return [{"type": "photo", "url": thumbnail_image_original}]

def get_media_url(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname != "twitter.com":
        raise ValueError("Not a Twitter URL")
    
    path_parts = parsed_url.path.split("/")
    if len(path_parts) < 4:
        raise ValueError("Invalid tweet URL")
    tweet_id = path_parts[3]

    query = {"id": tweet_id, "lang": "en"}
    new_url_parts = parsed_url._replace(scheme="https", netloc="cdn.syndication.twimg.com", path="/tweet-result", query=urlencode(query, True))
    new_url = urlunparse(new_url_parts)

    res = requests.get(new_url)
    res.raise_for_status()
    data = res.json()
    
    obj = data
    arr = []
    while True:
        if "mediaDetails" in obj:
            arr.extend(get_tweet_details(obj))
        if "card" in obj:
            arr.extend(get_card_details(obj))
        if "quoted_tweet" in obj:
            obj = obj["quoted_tweet"]
        else:
            break
    
    return arr