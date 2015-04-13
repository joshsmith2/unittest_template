from base import *


class AuthTest(GeneralTest):

    def test_can_pick_up_api_key_with_relative_path(self):
        key = public_api.get_api_key('./files/dummy_api_key')
        self.assertEqual('FFFFFFFFI8005cfn4Mhhhhhhhh2WI5m11114090', key)


class InputTest(GeneralTest):

    def test_can_get_help_when_running_script_from_cmd(self):
        output = sp.check_output([self.script, '-h'])
        self.assertIn("show this help message and exit", output)

class OutputTest(GeneralTest):

    def test_a_csv_file_can_be_output(self):
        leekspin = public_api.get_videos([self.leekspin_id])
        public_api.output_to_csv(leekspin, self.output)
        self.assertTrue(os.path.exists(self.output))

    def test_unicode_not_a_problem(self):
        dummy_vid = {'name': u'\u2019'}
        public_api.output_to_csv([dummy_vid], self.output)

class IdTest(GeneralTest):

    def test_can_get_proper_id_from_url(self):
        urls = ['https://www.youtube.com/watch?v=X9EbKV5yWMk',
                'https://www.youtube.com/watch?v=xy0GPL0s1vg&feature=youtu.be',
                'https://www.youtube.com/watch?v=y9C3Nj8qknk, http://www.sadiqkhan.org.uk/harrow_east',
                'https://youtu.be/1FDy0y8cPcY',
                'https://youtu.be/d2JVKeOExEE?t=46m36s',
                'http://youtube.com/watch?vi=dQw4w9WgXcQ&feature=youtube_gdata_player',
                'http://youtube.com/v/dQw4w9WgXcQ?feature=youtube_gdata_player']
        ids = ['X9EbKV5yWMk', 'xy0GPL0s1vg', 'y9C3Nj8qknk', '1FDy0y8cPcY',
               'd2JVKeOExEE', 'dQw4w9WgXcQ', 'dQw4w9WgXcQ']
        returned = [public_api.get_video_ids(url) for url in urls]
        self.assertEqual(returned, ids)

    def test_do_not_match_lists_or_channels(self):
        urls = ['https://www.youtube.com/playlist?list=PLeJ0kwUqFJGCHG_mEjC4M9EH1YhLqkSlr',
                'https://www.youtube.com/channel/UCg8AmXrkMhrwtqbkzSgfBDw']
        returned = [public_api.get_video_ids(url) for url in urls]
        self.assertEqual([None, None], returned)

    def test_can_get_ids_from_input_csv(self):
        expected = ['cZaGMKQ8-s4', '_dUwSshAz3Q', None, '1UkpzUdwpYY']
        result = public_api.get_ids_from_input_csv(self.test_csv)
        self.assertEqual(expected, result)


if __name__ == '__main__':
     unittest.main()
