"""
Flask API to extract media URLs from various platforms, such as Twitter and Instagram.
"""

from flask import Flask, request, jsonify
from platforms.twitter import get_media_url as get_twitter_media_url
from platforms.instagram import instagram_client

app = Flask(__name__)

@app.route('/api/get_media_url', methods=['POST'])
def api_get_media_url():
    """
    Extract media URLs from a given URL.
    """
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    platform = get_platform(url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 400

    try:
        media_urls = extract_media_url(url, platform)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 500

    return jsonify({'media_urls': media_urls})

def get_platform(url):
    """
    Return the platform of a given URL.
    """
    if 'twitter.com' in url:
        return 'twitter'
    elif 'instagram.com' in url:
        return 'instagram'
    # Add more platforms here as they are implemented
    else:
        return None

def extract_media_url(url, platform):
    """
    Extract media URLs from a given URL.
    """
    if platform == 'twitter':
        return get_twitter_media_url(url)
    elif platform == 'instagram':
        return instagram_client.get_media_url(url)
        return []
    else:
        raise ValueError('Unsupported platform')

if __name__ == '__main__':
    app.run(debug=True)
