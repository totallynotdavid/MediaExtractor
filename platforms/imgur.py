def get_mp4_url(url):
    """
    Replace .gifv extension in Imgur URLs with .mp4
    """
    if 'imgur.com' in url and url.endswith('.gifv'):
        return url.rsplit('.', 1)[0] + '.mp4'
    return url
