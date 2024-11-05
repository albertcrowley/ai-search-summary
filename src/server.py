from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import ollama
import logging
from urllib.parse import urlparse, unquote

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_url(url):
    """Check if the provided URL is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def extract_text_from_url(url):
    """Download and extract text content from the given URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text(separator=' ', strip=True)

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text
    except Exception as e:
        logger.error(f"Error extracting text from URL: {str(e)}")
        raise


def summarize_text(text):
    """Use Ollama to summarize the text."""
    try:
        prompt = f"Please provide a concise summary of the following text:\n\n{text}\n\nSummary:"
        response = ollama.generate(
            model='llama3.2',  # or your preferred model
            prompt=prompt
        )
        return response['response']
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise


def process_summary_request(url):
    """Common processing logic for both GET and POST requests."""
    try:
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # URL decode in case it's encoded
        url = unquote(url)

        if not is_valid_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400

        # Extract text from URL
        text = extract_text_from_url(url)

        if not text:
            return jsonify({'error': 'No content found at URL'}), 400

        # Generate summary
        summary = summarize_text(text)

        return jsonify({
            'url': url,
            'summary': summary
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error fetching URL: {str(e)}'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/summarize', methods=['GET', 'POST'])
def summarize_url():
    """Endpoint to accept URL and return summary via GET or POST."""
    if request.method == 'POST':
        data = request.get_json()
        url = data.get('url') if data else None
    else:  # GET method
        url = request.args.get('url')

    return process_summary_request(url)


if __name__ == '__main__':
    app.run(debug=True)