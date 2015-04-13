#!/usr/bin/env python2.7

import apiclient
import os
import sys
import argparse
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from datetime import datetime
from csv import DictWriter
from collections import OrderedDict

SOURCE_ROOT = os.path.dirname(os.path.realpath(__file__))
SECRETS_DIRECTORY = os.path.join(SOURCE_ROOT, 'secret')

def build_video_dict(api_response_item):
    """
    This is the dictionary which will store all analytics data.
    May (will) need refining.

    :param api_response_item: The output from a call to get_api_output
                              for one or more videos.
    """
    video = OrderedDict()

    # Get data from response
    snippet = api_response_item['snippet']
    statistics = api_response_item['statistics']
    video['id'] = api_response_item['id']

    # Snippet data
    video['name'] = snippet['title']

    video['channel_title'] = snippet['channelTitle']
    video['description'] = snippet['description']
    unicode_datetime = snippet['publishedAt']
    published_datetime_iso = unicode_datetime.encode('ascii')
    video['published_datetime_iso'] = published_datetime_iso
    published_datetime = datetime.strptime(published_datetime_iso,
                                           "%Y-%m-%dT%H:%M:%S.%fZ")
    video['published_datetime'] = published_datetime
    date_format = "%Y/%m/%d"
    time_format = "%H:%M:%S"
    video['published_date'] = published_datetime.strftime(date_format)
    video['published_time'] = published_datetime.strftime(time_format)

    # Statistics data
    video['comment_count'] = int(statistics['commentCount'])
    video['view_count'] = int(statistics['viewCount'])
    video['favourite_count'] = int(statistics['favoriteCount'])
    video['dislike_count'] = int(statistics['dislikeCount'])
    video['like_count'] = int(statistics['likeCount'])
    video['approval'] = video['like_count'] - video['dislike_count']

    return video

def get_videos(video_ids):
    videos = []
    response = make_api_call(video_ids)
    for item in response['items']:
        videos.append(build_video_dict(item))
    return videos

def make_api_call(video_ids):
    """
    Given a list of Youtube video ids, make an API call to pull back data
    concerning them

    :param video_ids: List of ids as strings
    :return: the API response
    """
    oauth_key_file = os.path.join(SECRETS_DIRECTORY, 'oauth_key.p12')
    creds = get_oath_credentials(oauth_key_file)

    http_auth = creds.authorize(Http())
    service = apiclient.discovery.build('youtube', 'v3',
                                             http=http_auth)
    response = service.videos().list(id=','.join(video_ids),
                                     part='snippet, statistics').execute()
    return response

#Not in git, for obvious reasons
def get_api_key(api_key_file):
    api_key_file = os.path.abspath(api_key_file)
    try:
        with open(api_key_file, 'r') as key_file:
            api_key = key_file.readline().strip()
        return api_key
    except IOError: # File not found
        print "%s does not exist - you need to create this yourself and " \
              "put a public API key in it. " % api_key_file
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
    p.add_argument('-o', '--output-file', metavar='PATH', dest="output_file",
                   help="Path to a .csv file which will hold the output of " \
                        "this query.")
    return p.parse_args()

def output_to_csv(videos, output_file):
    """
    :param videos: A list of videos to print to a .csv file
    """
    with open(output_file, 'w') as o_f:
        try:
            fieldnames = videos[0].keys()
        except IndexError:
            print "No videos passed to output_to_csv"
            return
        w = DictWriter(o_f, fieldnames=fieldnames)
        w.writeheader()
        for video in videos:
            w.writerow(video)

def main():
    args = get_arguments()
    output_to_csv(get_videos([args.id]), args.output_file)

if __name__ == '__main__':
    main()