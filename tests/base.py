import unittest
import os
import subprocess as sp

try:
    import public_api
except ImportError:
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    import public_api


class GeneralTest(unittest.TestCase):

    def setUp(self):

        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.leekspin_id = '1wnE4vF9CQ4'
        self.green_id = 'PPgS7p40ERg'
        self.test_directory = os.path.dirname(os.path.realpath(__file__))
        self.script = os.path.join(self.test_directory, '../public_api.py')
        self.output = os.path.join(self.test_directory, 'files', 'output.csv')
        self.test_csv = os.path.join(self.current_dir, 'files',
                                     'test_csv_in.csv')
        self.minimal_command = [self.script,
                                '-i', self.leekspin_id,
                                '-o', self.output]
        # Clear up from last run. Would do this is tearDown, but I like to have
        # the results sticking aroubnd (and ignored in git) for debugging
        # purposes
        if os.path.exists(self.output):
            os.remove(self.output)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()