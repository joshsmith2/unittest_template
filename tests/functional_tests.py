from base import *

class FunctionalTest(GeneralTest):

    def test_can_run_the_main_function_without_anything_bad_happening(self):
        public_api.main()

if __name__ == '__main__':
     unittest.main()