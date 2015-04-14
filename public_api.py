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

class ApiService:
    def __init__(self, key_type='oauth'):
        """
        param: key_type: One of 'oauth' or 'api'
        """

        if key_type == 'oauth':
            oauth_key_file = os.path.join(SECRETS_DIRECTORY, 'oauth_key.p12')
            creds = get_oath_credentials(oauth_key_file)
            http_auth = creds.authorize(Http())
            service = apiclient.discovery.build('youtube', 'v3',
                                                http=http_auth)
        elif key_type == 'api':
            public_api_key = get_api_key()
            service = apiclient.discovery.build('youtube', 'v3',
                                                 developerKey=public_api_key)

        else:
            raise ValueError("Key type not known. Must be one of 'oauth'"
                             "or 'api'")
        self.service = service

def parse_iso_datetime(time_to_convert):
    """
    :param time_to_convert: An iso datetime returned by google
    :return: A datetime object
    """
    return datetime.strptime(time_to_convert,"%Y-%m-%dT%H:%M:%S.%fZ")

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
    video['link'] = "youtu.be/" + str(video['id'])

    # Snippet data
    video['name'] = snippet['title']

    video['channel_title'] = snippet['channelTitle']
    trimmed_desc = snippet['description'].replace('\n',' ').replace('\r', ' ')
    video['description'] = trimmed_desc
    published_datetime_iso = snippet['publishedAt']
    video['published_datetime_iso'] = published_datetime_iso
    published_datetime = parse_iso_datetime(published_datetime_iso)
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

    # Comment data
    recent_comments = get_most_recent_comments(video['id'])
    most_liked_comment = sort_comments_by_likes(recent_comments)[0]['snippet']
    comment_inner = most_liked_comment['topLevelComment']['snippet']

    video['recent_liked_comment'] = comment_inner['textDisplay']
    video['recent_liked_comment_author'] = comment_inner['authorDisplayName']
    video['recent_liked_comment_like_count'] = comment_inner['likeCount']
    video['recent_liked_comment_reply_count'] = most_liked_comment['totalReplyCount']
    t = str(parse_iso_datetime(comment_inner['publishedAt']))
    video['recent_liked_comment_time'] = t

    most_replied_to_comment = sort_comments_by_replies(recent_comments)[0]['snippet']
    comment_inner = most_replied_to_comment['topLevelComment']['snippet']

    video['recent_replied_to_comment'] = comment_inner['textDisplay']
    video['recent_replied_to_comment_author'] = comment_inner['authorDisplayName']
    video['recent_replied_to_comment_like_count'] = comment_inner['likeCount']
    video['recent_replied_to_comment_reply_count'] = most_replied_to_comment['totalReplyCount']
    t = str(parse_iso_datetime(comment_inner['publishedAt']))
    video['recent_replied_to_comment_time'] = t

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
    api_service = ApiService().service
    vid_list_response = api_service.videos().list(id=','.join(video_ids),
                                                  part='snippet,'
                                                       'statistics').execute()
    for item in vid_list_response['items']:
        videos.append(build_video_dict(item))
    return videos

def get_most_recent_comments(video_id, count=100):
    """
    Return the first count comments from a video

    :param video_id: Id of video as string
    :param count: Number of comments to return as int. Currently needs to be between
                  0 and 100 due to Youtube data API restrictions
    :return: A list of comments, unadulterated
    """
    if count > 100 or count < 0:
        raise ValueError("Count must be between 0 and 100")
    api_service = ApiService(key_type='api').service
    return api_service.commentThreads().list(videoId=video_id,
                                             part='snippet',
                                             maxResults=count).execute()

def like_count(comment):
    return comment['snippet']['topLevelComment']['snippet']['likeCount']

def reply_count(comment):
    return comment['snippet']['totalReplyCount']

def sort_comments_by_likes(comments):
    """
    From a list of comment, get the most liked one

    :param comments: A list of comments, from get_most_recent_comments
    :return: All data for the single most liked comment
    """

    unsorted_comments = comments['items']
    return sorted(unsorted_comments, key=lambda c: like_count(c), reverse=True)

def sort_comments_by_replies(comments):
    """
    From a list of comment, get the most replied_to one

    :param comments: A list of comments, from get_most_recent_comments
    :return: All data for the single most replied_to comment
    """
    unsorted_comments = comments['items']
    return sorted(unsorted_comments,
                  key=lambda c: reply_count(c),
                  reverse=True)

#Not in git, for obvious reasons
def get_api_key(api_key_file=os.path.join(SECRETS_DIRECTORY,
                                          'public_api_key.key')):
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