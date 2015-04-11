from base import *
try:
    import public_api
except ImportError:
    import sys
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)
    import public_api


class AuthTest(GeneralTest):

    def test_can_pick_up_api_key_with_relative_path(self):
        key = public_api.get_api_key('./files/dummy_api_key')
        self.assertEqual('FFFFFFFFI8005cfn4Mhhhhhhhh2WI5m11114090', key)

class QueryTest(GeneralTest):

    def test_query_with_video_id_returns_a_response(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertNotEqual(leekspin.response, '')
        print leekspin.response

    def test_can_get_video_name_from_id(self):
        pass


if __name__ == '__main__':
     unittest.main()
