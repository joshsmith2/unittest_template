#!/usr/bin/env python2.7

import apiclient
import os
import sys
import argparse
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from datetime import datetime
from collections import OrderedDict
import dict_unicode_writer
import string
import re
import csv

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
    trimmed_desc = snippet['description'].replace('\n',' ').replace('\r', ' ')
    video['description'] = trimmed_desc
    published_datetime_iso = snippet['publishedAt']
    video['published_datetime_iso'] = published_datetime_iso
    published_datetime = datetime.strptime(published_datetime_iso,
                                           "%Y-%m-%dT%H:%M:%S.%fZ")
    video['published_datetime'] = str(published_datetime)
    date_format = "%d/%m/%Y"
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

def get_video_ids(url):
    """
    Given a Youtube url, return the id. This will probably need much tweaking
    as new formats are discovered

    :param url: Youtube URL in question, in any format
    :return: Youtube id as a string
    """
    # This string concocted to avoid matches with channels and lists, which
    # have longer ids at present.
    video_regex = "(?:v=|vi=)?(?:[^0-9A-Za-z]|\\b)" \
                  "(?P<id>[0-9A-Za-z_-]{11}(?![0-9A-Za-z]))"
    split_characters = '/?,&'
    translation = string.maketrans(split_characters, ' '*len(split_characters))
    split_url = string.translate(url, translation).split()
    for element in split_url:
        match = re.match(video_regex, element)
        if match:
            return match.group('id') # Returns first found. Might be an
                                     # issue later

def get_videos(video_ids):
    """
    Ties together the api call and video constructions to return a list of
    video data from a list of video ids

    :param video_ids: A list of video ids in string format
    :return: A list of dictionaries, each containing a lot of video data
    """
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
    p.add_argument('-i', '--id', metavar='STRING', dest='id',
                   help="For single videos, the id of the video to retrieve"
                        " stats for.")
    p.add_argument('-o', '--output-file', metavar='PATH', dest='output_file',
                   help="Path to a .csv file which will hold the output of " \
                        "this query.")
    p.add_argument('-c', '--csv-in', metavar='PATH', dest='csv_in',
                   help="Path to in .csv file containing a single row of "
                        "Youtube URLS. Supports every URL I've seen so far.")
    return p.parse_args()

def output_to_csv(videos, output_file):
    """
    :param videos: A list of videos to print to a .csv file
    """
    with open(output_file, 'w') as o_f:
        # BOM (optional...Excel needs it to open UTF-8 file properly)
        try:
            fieldnames = videos[0].keys()
        except IndexError:
            print "No videos passed to output_to_csv"
            return
        w = dict_unicode_writer.DictUnicodeWriter(o_f, fieldnames=fieldnames)
        w.writeheader()
        for video in videos:
            w.writerow(video)

def get_ids_from_input_csv(input_file):
    """
    :param csv: Path to a csv file containing Youtube URLs
    :return: A list of ids
    """
    ids = []
    with open(input_file, 'rU') as input_file:
        reader = csv.reader(input_file)
        for row in reader:
            video_id = get_video_ids(row[0])
            if video_id:
                ids.append(video_id)
    return ids

def chunks(l, n):
    """ Yield successive n-sized chunks from l.

    From http://stackoverflow.com/questions/312443/
    how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def main():
    args = get_arguments()
    videos = []
    if args.id:
        specified_id_video = get_videos([args.id])
        videos.extend(specified_id_video)
    if args.csv_in:
        csv_ids = get_ids_from_input_csv(args.csv_in)
        # Cut the videos up into chunks of 50, to avoid limits on HTTP requests
        generated_csv_chunks = chunks(csv_ids, 50)
        for g in generated_csv_chunks:
            csv_videos = get_videos(g)
            videos.extend(csv_videos)
    output_to_csv(videos, args.output_file)

if __name__ == '__main__':
    main()