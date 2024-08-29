import requests
import time

# Define the URL and headers
url = "http://localhost:7777/parcelle_rapport?parcelle=67482000BA0610&token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI3MTE2NzU5LCJpYXQiOjE3MjQ1MjQ3NTksImp0aSI6IjAwYzI3N2JiM2JhOTQ4ZmQ4Yjk4YzEwMjNjNjlmMDk2IiwidXNlcl9uYW1lIjoiY2xlbWVudC56aXRvdW5pQHN0cmFzYm91cmcuZXUiLCJhdWQiOiJhcGlkZiJ9.6U6bZzU_9S65cyyJ1D4-6JMqb_Xfb6bytX_MqwpUdGw"
headers = {"X-User-ID": "12345"}  # Simulate a user with ID 12345

# Number of requests to send
num_requests = 105

# Store the responses
responses = []

# Send multiple requests
for i in range(num_requests):
    response = requests.get(url, headers=headers)
    responses.append((i+1, response.status_code))
    print(f"Request {i+1}: HTTP {response.status_code}")

    # Sleep for a short time between requests (if needed)
    time.sleep(0.1)  # Adjust the sleep time to control the speed of requests

# Output the results
for i, status_code in responses:
    print(f"Request {i}: HTTP {status_code}")
