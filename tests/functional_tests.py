from base import *

class FunctionalTest(GeneralTest):

    def test_can_get_output_from_leekspin(self):
        # Someome runs the function to find out what's up with Leekspin these
        # days.
        sp.check_call(self.minimal_command)

        # A file is output. It's a .csv file
        self.assertTrue(os.path.exists(self.output))

        # In that file is a header row, comma seperated, and some data
        with open(self.output, 'r') as f:
            contents = f.readlines()
        self.assertEqual(len(contents), 2)

        # They contain pretty much what you'd expect
        headers = contents[0].split(',')
        results = contents[1].split(',')
        for header in ['name', 'view_count', 'comment_count']:
            self.assertIn(header, headers)
        for result in ['Leek Spin', 'Xyliex', '2006/09/26']:
            self.assertIn(result, results)


if __name__ == '__main__':
     unittest.main()