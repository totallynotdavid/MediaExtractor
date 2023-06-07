import requests
import logging

logger = logging.getLogger(__name__)

class RedGifs:
    _FORMATS = {
        'gif': 250,
        'sd': 480,
        'hd': None,
    }

    def __init__(self):
        self.headers = {
            'referer': 'https://www.redgifs.com/',
            'origin': 'https://www.redgifs.com',
            'content-type': 'application/json',
        }
        self.api_url = 'https://api.redgifs.com/v2'
    
    def fetch_oauth_token(self):
        try:
            response = requests.get(f'{self.api_url}/auth/temporary', headers=self.headers)
            response.raise_for_status()

            token_data = response.json()
            self.headers['authorization'] = f'Bearer {token_data["token"]}'
        except (requests.HTTPError, KeyError) as e:
            logger.error("Failed to fetch oauth token: %s", e)
            raise Exception('Unable to get temporary token')

    def get_high_quality_url(self, video_id):
        if 'authorization' not in self.headers:
            self.fetch_oauth_token()

        try:
            video_info = requests.get(f'{self.api_url}/gifs/{video_id}?views=yes', headers=self.headers)
            video_info.raise_for_status()

            gif_data = video_info.json()['gif']
            formats = self._get_gif_data(gif_data)

            high_quality_format = [f for f in formats if f['format_id'] == 'hd']
            return high_quality_format[0]['url'] if high_quality_format else None
        except (requests.HTTPError, KeyError) as e:
            logger.error("Failed to fetch high quality URL: %s", e)
            return None

    def _get_gif_data(self, video):
        orig_height = video.get('height')
        aspect_ratio = orig_height / video['width'] if video.get('width') else None

        formats = []
        for format_id, height in self._FORMATS.items():
            video_url = video['urls'].get(format_id)
            if not video_url:
                continue
            height = min(orig_height, height or orig_height)
            formats.append({
                'url': video_url,
                'format_id': format_id,
                'width': height * aspect_ratio if aspect_ratio else None,
                'height': height,
            })
        return formats
