import unittest
import os

class GeneralTest(unittest.TestCase):

    def setUp(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()