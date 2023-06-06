def get_best_quality_url(url):
    """
    Convert a Gfycat mobile-quality URL to the corresponding high-quality URL.
    """
    if 'thumbs.gfycat.com' in url and url.endswith('-mobile.mp4'):
        return url.replace('thumbs.', 'zippy.').replace('-mobile', '')
    return url
