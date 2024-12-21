import unittest
from unittest.mock import patch
from io import StringIO
from ASK_USER import ask_user

class TestAskUser(unittest.TestCase):
    @patch('builtins.input', return_value='test input')
    def test_ask_user_normal_input(self, mock_input):
        result = ask_user("Enter something")
        self.assertEqual(result, 'test input')

    @patch('builtins.input', return_value='')
    def test_ask_user_empty_input_with_default(self, mock_input):
        result = ask_user("Enter something", default="default value")
        self.assertEqual(result, 'default value')

    @patch('builtins.input', side_effect=EOFError)
    def test_ask_user_eof_error(self, mock_input):
        with self.assertRaises(EOFError):
            ask_user("Enter something")

if __name__ == '__main__':
    unittest.main()