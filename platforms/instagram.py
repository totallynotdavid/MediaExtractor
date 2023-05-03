import os
from instagrapi import Client

def get_media_url(url, email, password):
    client = Client()
    client.login(email, password)
    media_id = client.media_pk_from_url(url)
    media = client.media_info(media_id)
    return media.thumbnail_url, media.video_url