#!/usr/bin/env python2.7

import apiclient
import os
import sys
import argparse
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from datetime import datetime

SOURCE_ROOT = os.path.dirname(os.path.realpath(__file__))
SECRETS_DIRECTORY = os.path.join(SOURCE_ROOT, 'secret')


class AuthObject:
    """
    Either an OAuth2 token or public API key.
    HALF BAKED
    """
    def __init__(self, type, credentials_file, client_email=None):
        """
        :param type: Credentials type - one of OAuth2 or Public
        :param credentials_file:  File holding credentials
        :param client_email: Optional. Required for OAuth2
        """
        self.type = type
        self.credentials_file = credentials_file
        self.client_email = client_email
        if type == "OAuth2":
            pass


class Video:
    def __init__(self, id):
        """
        This is the object which will store all analytics data.
        May (will) need refining.

        :param id: Youtube id for the video to be examined
        :param start_date: Start date in YYYY-MM-DD format
        :param end_date: See start date
        """
        oauth_key_file = os.path.join(SECRETS_DIRECTORY, 'oauth_key.p12')
        creds = get_oath_credentials(oauth_key_file)

        self.http_auth = creds.authorize(Http())
        self.service = apiclient.discovery.build('youtube', 'v3',
                                                 http=self.http_auth)
        self.response = self.service.videos().list(
            id=id,
            part='snippet, statistics').execute()

        snippet = self.response['items'][0]['snippet']
        statistics = self.response['items'][0]['statistics']

        # Snippet data
        self.name = snippet['title']
        unicode_datetime = snippet['publishedAt']
        self.published_datetime_iso = unicode_datetime.encode('ascii')
        published_datetime = datetime.strptime(self.published_datetime_iso,
                                               "%Y-%m-%dT%H:%M:%S.%fZ")
        date_format = "%Y/%m/%d"
        time_format = "%H:%M:%S"
        self.published_date = published_datetime.strftime(date_format)
        self.published_time = published_datetime.strftime(time_format)
        self.channel_title = snippet['channelTitle']

        # Statistics data
        self.comment_count = int(statistics['commentCount'])
        self.view_count = int(statistics['viewCount'])
        self.favourite_count = int(statistics['favoriteCount'])
        self.dislike_count = int(statistics['dislikeCount'])
        self.like_count = int(statistics['likeCount'])
        self.approval = self.like_count - self.dislike_count


#Not in git, for obvious reasons
def get_api_key(api_key_file):
    api_key_file = os.path.abspath(api_key_file)
    try:
        with open(api_key_file, 'r') as key_file:
            api_key = key_file.readline().strip()
        return api_key
    except IOError: # File not found
        print "%s does not exist - you need to create this yourself and put a " \
              "public API key in it. " % api_key_file
        sys.exit(1)

def get_oath_credentials(key_file, client_email_file=None):
    """
    :param key_file: Contains OAuth2 private key, in .p12 format
    :param client_email_file: Conatins client email (from Developers console)
    :return: SignedJwtAssertionCredentials object

    Help here from
    https://developers.google.com/identity/protocols/OAuth2ServiceAccount
    """

    # Set default client_email file if not defined.
    if not client_email_file:
        client_email_file = os.path.join(SECRETS_DIRECTORY, 'client_email.txt')
    with open(client_email_file, 'r') as f:
        client_email = f.read()
    with open(key_file, 'r') as f:
        private_key = f.read()
    credentials = SignedJwtAssertionCredentials(client_email, private_key,
                 'https://www.googleapis.com/auth/youtube.readonly')
    return credentials

def get_arguments():
    blurb = "Returns a host of information concerning a youtube video, " \
            "given its ID."
    p = argparse.ArgumentParser(description=blurb)
    p.add_argument('-i', '--id', metavar='STRING', dest="id",
                   help="For single videos, the id of the video to retrieve"
                        " stats for.")
    return p.parse_args()

def main():
    get_arguments()

if __name__ == '__main__':
    main()