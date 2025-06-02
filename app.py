from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/get_leaderboard")
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
