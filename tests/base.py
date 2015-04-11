import unittest
import os
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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()