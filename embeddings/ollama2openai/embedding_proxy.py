from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configure the URL for the OLLAMA server
OLLAMA_EMBEDDING_URL = 'http://localhost:11434/api/embeddings'

# Specify the header name for authorization
AUTH_HEADER_NAME = "Authorization"

@app.route('/api/embeddings', methods=['POST'])
def proxy_request():
    # Extract the incoming data from the original request
    input_data = request.get_json()
    text_input = input_data.get('input')
    model_type = input_data.get('model')
    # Extract the Authorization header from the incoming request, if it exists
    auth_header = request.headers.get(AUTH_HEADER_NAME)
    # Headers to forward
    headers = {}
    if auth_header:
        headers[AUTH_HEADER_NAME] = auth_header
    # Transform the request to match the schema of the destination API
    payload = {
        "model": model_type,
        "prompt": text_input
    }
    # Forward the request to the other server
    response = requests.post(OLLAMA_EMBEDDING_URL, json=payload, headers=headers)
    # Check if the request was successful
    if response.status_code == 200:
        # Transform the response to match the expected output schema
        response_data = response.json()
        transformed_response = {
            "object": "list",
            "data": [{
                "object": "embedding",
                "index": 0,
                "embedding": response_data['embedding']
            }],
            "model": model_type,
            "usage": {
                "prompt_tokens": len(text_input.split()),  # Simplified token counting
                "total_tokens": len(text_input.split())
            }
        }
        return jsonify(transformed_response)
    else:
        # Handle errors or unsuccessful status codes
        return jsonify({"error": "Failed to retrieve embeddings"}), response.status_code
if __name__ == '__main__':
    app.run()
