from base import *
import subprocess as sp


class AuthTest(GeneralTest):

    def test_can_pick_up_api_key_with_relative_path(self):
        key = public_api.get_api_key('./files/dummy_api_key')
        self.assertEqual('FFFFFFFFI8005cfn4Mhhhhhhhh2WI5m11114090', key)

class QueryTest(GeneralTest):

    def test_query_with_video_id_returns_a_response(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertNotEqual(leekspin.response, '')

    def test_can_get_video_name_from_id(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertEqual(u'Leek Spin', leekspin.name)

    def test_can_get_channel_name_from_id(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertEqual(u'Xyliex', leekspin.channel_title)

    def test_can_get_video_published_time_and_date_in_multiple_formats(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertEqual('2006-09-26T02:45:35.000Z',
                         leekspin.published_datetime_iso)
        self.assertEqual('2006/09/26', leekspin.published_date)
        self.assertEqual('02:45:35', leekspin.published_time)

    def test_can_get_view_comment_favourite_statistics(self):
        leekspin = public_api.Video(self.leekspin_id)
        self.assertLessEqual(18150, leekspin.comment_count)
        self.assertLessEqual(6475867, leekspin.view_count)
        self.assertLessEqual(0, leekspin.favourite_count)
        self.assertLessEqual(1120, leekspin.dislike_count)
        self.assertLessEqual(31661, leekspin.like_count)
        self.assertEqual(leekspin.like_count - leekspin.dislike_count,
                         leekspin.approval)

class InputTest(GeneralTest):

    def test_can_get_help_when_running_script_from_cmd(self):
        output = sp.check_output(self.minimal_command)
        self.assertIn("show this help message and exit", output)

if __name__ == '__main__':
     unittest.main()
