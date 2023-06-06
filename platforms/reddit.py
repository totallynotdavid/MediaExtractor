import requests
import logging

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0'

def get_media_url(url):
    """
    Extract media URLs from a given Reddit URL.
    """
    try:
        response = _fetch_reddit_data(url)
        data = response.json()
    except Exception as e:
        logger.error("Failed to fetch reddit data: %s", e)
        return []

    try:
        media_urls = _extract_media_urls(data)
    except Exception as e:
        logger.error("Failed to extract media URLs: %s", e)
        return []

    return media_urls

def _fetch_reddit_data(url):
    if not url.endswith('.json'):
        url += '.json'
    headers = {'User-Agent': USER_AGENT}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.content}")

    return response

def _extract_media_urls(data):
    media_urls = []

    for post_data in _iterate_posts(data):
        media_urls += _get_post_media_urls(post_data)

    return media_urls

def _iterate_posts(data):
    if 'data' in data[0] and 'children' in data[0]['data']:
        for post in data[0]['data']['children']:
            yield post['data']

def _get_post_media_urls(post_data):
    media_urls = []
    post_hint = post_data.get('post_hint')

    if post_hint == 'image':
        media_urls.append(post_data['url'])
    elif post_hint == 'hosted:video':
        media_urls.append(post_data['media']['reddit_video']['fallback_url'])
    elif post_hint in ['rich:video', 'link']:
        if 'preview' in post_data and 'images' in post_data['preview']:
            for image in post_data['preview']['images']:
                media_urls.append(image['source']['url'])
        elif 'thumbnail' in post_data:
            media_urls.append(post_data['thumbnail'])
    elif post_hint == 'gallery':
        if 'gallery_data' in post_data:
            for item in post_data['gallery_data']['items']:
                media_id = item['media_id']
                if media_id in post_data['media_metadata']:
                    media_urls.append(post_data['media_metadata'][media_id]['p'])

    return media_urls