from base import *
try:
    import main
except ImportError:
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    import main

class UnitTest(GeneralTest):

    def test_goes_here(self):
        self.assertTrue(True)

if __name__ == '__main__':
     unittest.main()
