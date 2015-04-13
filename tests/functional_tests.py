from base import *

class FunctionalTest(GeneralTest):

    def test_can_get_output_from_green_video(self):
        # Someome runs the function to find out what's up with the Greens these
        # days.
        sp.check_call([self.script,
                      '-i', self.green_id,
                      '-o', self.output])

        # A file is output. It's a .csv file
        self.assertTrue(os.path.exists(self.output))

        # In that file is a header row, comma separated, and some data
        with open(self.output, 'r') as f:
            contents = f.readlines()
        self.assertEqual(len(contents), 2)

        # They contain pretty much what you'd expect
        headers = contents[0].split(',')
        results = contents[1].split(',')
        for header in ['name', 'view_count', 'comment_count']:
            self.assertIn(header, headers)
        green_title = 'Change The Tune - Green Party 2015 Election Broadcast'
        green_user = 'Green Party of England & Wales'
        for result in [green_title, green_user, '08/04/2015']:
            self.assertIn(result, results)


if __name__ == '__main__':
     unittest.main()