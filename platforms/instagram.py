"""
Module to handle Instagram media extraction using the instagrapi package.
"""

import os
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv(dotenv_path='./.env')

class InstagramClient:
    """
    Class to handle Instagram media extraction using the instagrapi package.
    """
    def __init__(self, email, password):
        self.client = Client()
        self.client.login(email, password)

    def get_media_url(self, url):
        """
        Return the media URL from a given Instagram URL.
        """
        media_id = self.client.media_pk_from_url(url)
        media = self.client.media_info(media_id)

        urls = []

        if media.media_type == 8:
            print("Detected gallery")  
            for item in media.resources:
                print(f"Resource Info: {item}")  
                urls.append(item.thumbnail_url)
        elif media.media_type == 1:
            print("Detected image")  
            urls.append(media.thumbnail_url)
        elif media.media_type == 2:
            print("Detected video")  
            urls.append(media.video_url)

        return urls

INSTAGRAM_EMAIL = os.environ.get("INSTAGRAM_EMAIL")
INSTAGRAM_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")
instagram_client = InstagramClient(INSTAGRAM_EMAIL, INSTAGRAM_PASSWORD)
