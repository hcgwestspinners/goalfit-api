from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from functools import wraps
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # 👈 This allows requests from any origin

a
# Configuration
REQUEST_TIMEOUT = 10  # seconds
MAX_RETRIES = 3

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.RequestException as e:
            return jsonify({"error": f"Network error: {str(e)}"}), 503
        except Exception as e:
            return jsonify({"error": f"Server error: {str(e)}"}), 500
    return wrapper

def get_session():
    session = requests.Session()
    session.timeout = REQUEST_TIMEOUT
    return session

@app.route("/")
def home():
    return jsonify({
        "status": "API is running",
        "endpoints": {
            "leaderboard": "/get_leaderboard"
        }
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint does not exist",
        "available_endpoints": ["/", "/get_leaderboard"]
    }), 404

@app.route("/get_leaderboard")
@handle_errors
def get_leaderboard():
    email = "hcgwestspinners@gmail.com"
    password = "#cgWe$tCylist@123"

    login_url = "https://www.app.goals.fit/api/v11/sign_in"
    payload = {"user": {"email": email, "password": password}}
    session = requests.Session()
    r = session.post(login_url, json=payload)

    if r.status_code != 200:
        return jsonify({"error": "Login failed"}), 403

    token = r.json()['user']['authentication_token']
    user_id = str(r.json()['user_id'])

    session.cookies.set('athfe_email', email, domain='.goals.fit')
    session.cookies.set('athfe_id', user_id, domain='.goals.fit')
    session.cookies.set('athfe_token', token, domain='.goals.fit')

    page = session.get("https://admin.goals.fit/participants.php?cid=1523")
    soup = BeautifulSoup(page.text, 'html.parser')

    rows = soup.select("table tr")[1:]
    result = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            result.append({
                "rank": cols[0].text.strip(),
                "name": cols[1].text.strip().replace("\n", " "),
                "climb": cols[2].text.strip()
            })

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False) 

