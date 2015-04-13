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

    def test_can_get_output_from_csv_file(self):
        # We have a single rowed file full of URLs, and we feed it to our
        # script.
        csv_in = os.path.join(self.current_dir, 'files', 'test_csv_in.csv')
        sp.check_call([self.script,
                       '-c', csv_in,
                       '-o', self.output])

        # There's a file output...
        self.assertTrue(os.path.exists(self.output))

        # ...with 3 results in it (and a header)
        with open(self.output, 'r') as f:
            contents = f.readlines()
        self.assertEqual(len(contents), 4)
        headers = contents[0].split(',')
        results = [c.split(',') for c in contents [1:]]
        for header in ['name', 'view_count', 'comment_count']:
            self.assertIn(header, headers)

        # Further, these are the videos we'd expected to see
        names = ['George Galloway MP on Chilcot Inquiry Delays',
                 'Parliamentary Debate on Epilepsy - 26th February',
                 "Forced Marriage - It's Never OK."]
        for name in names:
            self.assertIn(name, results)

if __name__ == '__main__':
     unittest.main()