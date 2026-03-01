import requests
import os
API_URL = os.environ["API_URL"]

def make_request():
    response = requests.get(API_URL, timeout=500)
    print("Status:", response.status_code)
    print("Response:", response.text[:200])

if __name__ == "__main__":
    make_request()
