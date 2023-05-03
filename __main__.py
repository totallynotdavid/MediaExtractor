from flask import Flask, request, jsonify
from platforms.twitter import get_media_url as get_twitter_media_url

app = Flask(__name__)

@app.route('/api/get_media_url', methods=['POST'])
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'media_urls': media_urls})

def get_platform(url):
    if 'twitter.com' in url:
        return 'twitter'
    # Add more platforms here as they are implemented
    else:
        return None

def extract_media_url(url, platform):
    if platform == 'twitter':
        return get_twitter_media_url(url)
    # Add more platforms here as they are implemented
    else:
        raise Exception('Unsupported platform')

if __name__ == '__main__':
    app.run(debug=True)
