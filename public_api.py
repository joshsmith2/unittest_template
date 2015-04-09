import apiclient
import os
import sys

SOURCE_ROOT = os.path.dirname(os.path.realpath(__file__))

class Video:
    def __init__(self, id, api_key):
        self.service = apiclient.discovery.build('youtubeAnalytics', 'v1', api_key)
        self.views = self.service.metrics().query(
            id = id,
            metrics = 'views').execute()

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



def main():
    api_key = get_api_key(os.path.join(SOURCE_ROOT,
                                       'secret',
                                       'public_api_key.key'))

if __name__ == '__main__':
    main()