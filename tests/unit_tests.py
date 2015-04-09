from base import *


class AuthTest(GeneralTest):

    def test_can_pick_up_api_key_with_relative_path(self):
        key = public_api.get_api_key('./files/dummy_api_key')
        self.assertEqual('FFFFFFFFI8005cfn4Mhhhhhhhh2WI5m11114090', key)


    def test_loituma_query(self):
        leekspin_id = '1wnE4vF9CQ4'
        api_key = public_api.get_api_key(os.path.join(public_api.SOURCE_ROOT,
                                                      'public_api_key.key'))
        leekspin = public_api.Video(leekspin_id, api_key)
        self.assertNotEqual(leekspin.views, '')
        print leekspin.views

if __name__ == '__main__':
     unittest.main()
