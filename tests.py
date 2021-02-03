import unittest
import xmlrunner


class TestMethods(unittest.TestCase):
    def test_dummy(self):
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
