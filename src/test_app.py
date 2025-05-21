import unittest
from unittest.mock import patch
from . import app # To access app.summary_cache
from .app import summarize_text

class TestSummarizeTextCaching(unittest.TestCase):

    @patch('src.app.os.getenv')
    @patch('src.app.ollama.Client') # Path to ollama.Client needs to be from perspective of where tests are run
    def test_repeated_calls_use_cache(self, mock_ollama_client_constructor, mock_getenv):
        # Mock os.getenv to return a dummy URL
        mock_getenv.return_value = 'http://dummy_ollama_host:11434'

        # Configure the mock client instance and its generate method
        mock_client_instance = mock_ollama_client_constructor.return_value
        mock_client_instance.generate.return_value = {'response': 'mocked summary'}

        # Clear cache before test
        app.summary_cache = {}

        text = "some test text"
        
        # First call - should call Ollama
        summary1 = summarize_text(text)
        
        # Second call - should use cache
        summary2 = summarize_text(text)

        # Assertions
        self.assertEqual(mock_client_instance.generate.call_count, 1, "Ollama client's generate method should be called once.")
        self.assertEqual(summary1, 'mocked summary', "First call should return the mocked summary.")
        self.assertEqual(summary2, 'mocked summary', "Second call should also return the mocked summary from cache.")

    @patch('src.app.os.getenv')
    @patch('src.app.ollama.Client') # Path to ollama.Client needs to be from perspective of where tests are run
    def test_different_texts_call_api_separately(self, mock_ollama_client_constructor, mock_getenv):
        # Mock os.getenv to return a dummy URL
        mock_getenv.return_value = 'http://dummy_ollama_host:11434'

        # Configure the mock client instance and its generate method with side_effect
        mock_client_instance = mock_ollama_client_constructor.return_value
        def side_effect_func(model, prompt):
            # Simulate different summaries based on the prompt content
            if "first unique text" in prompt:
                return {'response': 'summary for first text'}
            elif "second unique text" in prompt:
                return {'response': 'summary for second text'}
            return {'response': 'default summary'}
            
        mock_client_instance.generate.side_effect = side_effect_func

        # Clear cache before test
        app.summary_cache = {}

        text1 = "first unique text"
        text2 = "second unique text"

        # First call for the first text
        summary1 = summarize_text(text1)

        # Second call for the second text
        summary2 = summarize_text(text2)

        # Assertions
        self.assertEqual(mock_client_instance.generate.call_count, 2, "Ollama client's generate method should be called twice for different texts.")
        self.assertEqual(summary1, 'summary for first text', "Summary for the first text is incorrect.")
        self.assertEqual(summary2, 'summary for second text', "Summary for the second text is incorrect.")
        self.assertNotEqual(summary1, summary2, "Summaries for different texts should be different.")

if __name__ == '__main__':
    unittest.main()
