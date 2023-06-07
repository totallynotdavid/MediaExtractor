import requests
import re

def get_best_quality_url(url):
    """
    Convert a Gfycat URL to the corresponding high-quality URL
    """
    if 'gfycat.com' in url:
        gfycat_id_match = re.search(r'gfycat.com/([\w-]+)', url)
        if gfycat_id_match:
            gfycat_id = gfycat_id_match.group(1)
            gfycat_id = gfycat_id.split('-')[0]  # Get the first part of the ID before any dashes
            
            gfy_info = requests.get(f'https://api.gfycat.com/v1/gfycats/{gfycat_id}').json()
            gfy_item = gfy_info.get('gfyItem', {})

            if 'error' in gfy_item:
                raise ValueError(f"Gfycat API error: {gfy_item['error']}")

            return gfy_item.get('mp4Url', url)
    return url
