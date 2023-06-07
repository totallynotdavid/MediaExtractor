"""
Flask API to extract media URLs from various platforms, such as Twitter and Instagram.
"""

# API
from flask import Flask, request, jsonify, Response, stream_with_context

# Platforms
from platforms.twitter import get_media_url as get_twitter_media_url
from platforms.reddit import get_media_url as get_reddit_media_url
from platforms.imgur import get_mp4_url as get_imgur_mp4_url
from platforms.gfycat import get_best_quality_url as get_gfycat_best_quality_url
from platforms.redgifs import RedGifs as RedGifs
from platforms.instagram import instagram_client

# Tools
import requests
import os
import logging

# Logging and caching
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)

@app.route('/api/get_media_url', methods=['POST'])
@limiter.limit("1000/day;100/hour;50/minute")
def api_get_media_url():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    platform = get_platform(url)
    if not platform:
        return jsonify({'error': 'Unsupported platform'}), 400

    try:
        media_urls = extract_media_url(url, platform)
    except Exception as exc:
        app.logger.error(f'Failed to extract media URLs for {url} due to {exc}')
        return jsonify({'error': str(exc)}), 500

    return jsonify({'media_urls': media_urls})

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

def get_platform(url):
    """
    Return the platform of a given URL.
    """
    if 'twitter.com' in url:
        return 'twitter'
    elif 'instagram.com' in url:
        return 'instagram'
    elif 'reddit.com' in url:
        return 'reddit'
    elif 'imgur.com' in url:
        return 'imgur'
    elif 'gfycat.com' in url:
        return 'gfycat'
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
    elif platform == 'reddit':
        return get_reddit_media_url(url)
    elif platform == 'imgur':
        return get_imgur_mp4_url(url)
    elif platform == 'gfycat':
        return [get_gfycat_best_quality_url(url)]
    else:
        raise ValueError('Unsupported platform')

# Instagram streaming
@app.route('/api/instagram/<video_id>', methods=['GET'])
def api_instagram(video_id):
    video_url = instagram_client.get_media_url_by_id(video_id)

    if not video_url:
        return jsonify({'error': 'Failed to fetch video URL'}), 400

    req = requests.get(video_url, stream=True)

    def generate():
        for chunk in req.iter_content(chunk_size=1024):
            yield chunk

    return Response(stream_with_context(generate()), content_type=req.headers['content-type'])

# Redgifs streaming
@app.route('/api/redgifs/<video_id>', methods=['GET'])
def api_redgifs(video_id):
    rg = RedGifs()
    high_quality_url = rg.get_high_quality_url(video_id)

    if not high_quality_url:
        return jsonify({'error': 'Failed to fetch high quality URL'}), 400

    req = requests.get(high_quality_url, stream=True)

    def generate():
        for chunk in req.iter_content(chunk_size=1024):
            yield chunk

    return Response(stream_with_context(generate()), content_type=req.headers['content-type'])

if __name__ == '__main__':
    debug_mode = bool(os.getenv("DEBUG_MODE", False))
    app.run(debug=True)