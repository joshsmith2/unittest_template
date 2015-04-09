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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()