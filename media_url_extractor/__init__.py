"""
Flask API to extract media URLs from various platforms, such as Twitter and Instagram.
"""

# Tools
import logging

# Standard libraries
import os
import requests

# API
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Platforms
from platforms.twitter import get_media_url as get_twitter_media_url
from platforms.reddit import get_media_url as get_reddit_media_url
from platforms.imgur import get_mp4_url as get_imgur_mp4_url
from platforms.gfycat import get_best_quality_url as get_gfycat_best_quality_url
from platforms.redgifs import RedGifs
from platforms.instagram import InstagramClient

app = Flask(__name__)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
instagram_client = InstagramClient()


@app.route('/api/get_media_url', methods=['POST'])
@limiter.limit("1000/day;100/hour;50/minute")
def api_get_media_url():
    """Get media URLs endpoint"""
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
        app.logger.error('Failed to extract media URLs for %s due to %s', url, exc)
        return jsonify({'error': str(exc)}), 500

    return jsonify({'media_urls': media_urls})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint to check the health of the service"""
    return jsonify({'status': 'healthy'}), 200

def get_platform(url):
    """Return the platform of a given URL."""
    if 'twitter.com' in url:
        return 'twitter'
    if 'instagram.com' in url:
        return 'instagram'
    if 'reddit.com' in url:
        return 'reddit'
    if 'imgur.com' in url:
        return 'imgur'
    if 'gfycat.com' in url:
        return 'gfycat'

def extract_media_url(url, platform):
    """Extract media URLs from a given URL."""
    if platform == 'twitter':
        return get_twitter_media_url(url)
    if platform == 'instagram':
        return instagram_client.get_media_url(url)
    if platform == 'reddit':
        return get_reddit_media_url(url)
    if platform == 'imgur':
        return get_imgur_mp4_url(url)
    if platform == 'gfycat':
        return [get_gfycat_best_quality_url(url)]
    return None

@app.route('/api/instagram/<video_id>', methods=['GET'])
def api_instagram(video_id):
    """Endpoint for Instagram streaming"""
    video_url = instagram_client.get_media_url_by_id(video_id)

    if not video_url:
        return jsonify({'error': 'Failed to fetch video URL'}), 400

    req = requests.get(video_url, stream=True, timeout=5.0)

    def generate():
        for chunk in req.iter_content(chunk_size=1024):
            yield chunk

    return Response(stream_with_context(generate()), content_type=req.headers['content-type'])

@app.route('/api/redgifs/<video_id>', methods=['GET'])
def api_redgifs(video_id):
    """Endpoint for Redgifs streaming"""
    red_gifs = RedGifs()
    high_quality_url = red_gifs.get_high_quality_url(video_id)

    if not high_quality_url:
        return jsonify({'error': 'Failed to fetch high quality URL'}), 400

    req = requests.get(high_quality_url, stream=True, timeout=5.0)

    def generate():
        for chunk in req.iter_content(chunk_size=1024):
            yield chunk

    return Response(stream_with_context(generate()), content_type=req.headers['content-type'])

if __name__ == '__main__':
    debug_mode = os.getenv("DEBUG_MODE", "False").lower() in ['true', '1']
    app.run(debug=debug_mode)
