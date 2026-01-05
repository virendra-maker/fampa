# app.py
from flask import Flask, request, jsonify, make_response
import requests
import random
import os

app = Flask(__name__)

OFFICIAL_API_HOST = "https://westeros.famapp.in"
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoidDQta3N4bE9pQmQ5d0VCWTRza3BmQVNkM1J3RHYyUWI1U3B2cmJEbWVVWWtubHBnWWtlWFEtU3FVWkVITzZBcGVqTnJ6SGxPOUdvIn0sImFsZyI6IkVDREgtRVMifQ..4zww34voRaVXMOqJjnBJtg.6g_QjERM9tuKNwJN-lnbnLr811XrVl6veOMx0wvyimvcF16TNBGjSabGiZJsDTwX0ZiHXVyWGuanjkaPKEjDQCHiZ4J97WKHK4lPpMlUTAV4RRzw4kNI5ZPOnMJ7DOQJlFtsOCobnF9Rv8JKoQKkHl7PDphDy16kOWpaov-zQ-76eY8ONplYNkZbG0sOYjlzK68-9gZa5V3dwQjf67f7jNwhhS3KZrLtf0gSPlxS7URynCbOOa75eKNgAXrTOXaEgUPO2w_pr8xQgrfB-Rto3ObMvb7y_DE99C06mS7MUktzLDW8agLhBDM-ti1m65H9K-De41iiCtv-PH1z9_g-xbwlWnaQDPKYITFYiryUpzcEfLBG4zYcA4Va8a82_yt-.zaENNo7SpZQXnuHoYPUahrqJblvnViVbaqulutcAiwY")
DEVICE_ID = os.environ.get("DEVICE_ID", "3a684c1812924cc8")
USER_AGENT = os.environ.get("USER_AGENT", "V2253 | Android 15 | Dalvik/2.1.0 | V2225 | 775D9A60776C7918DA72AF1AE73D5C1A0B131E36 | 3.11.5 (Build 525) | U78TN5J23U")

# Initialize session
SESSION = None

def init_session():
    """Initialize session with headers"""
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        SESSION.headers.update({
            "host": "westeros.famapp.in",
            "user-agent": USER_AGENT,
            "x-device-details": USER_AGENT,
            "x-app-version": "525",
            "x-platform": "1",
            "device-id": DEVICE_ID,
            "authorization": f"Token {AUTH_TOKEN}",
            "accept-encoding": "gzip",
            "content-type": "application/json; charset=UTF-8"
        })

CREDITS = [
    "#code was made by @we_are_cutehack",
    "#code was made by chx",
    "#code was made by cutehack",
    "#tumlog credit chor ho iss liye ye lga diya",
    "#koi bhe paid code banwana ho to cutehack ko jarur batao",
    "#code cutehack dwara banaya gya hai",
]

HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"

def _pick_credit():
    return random.choice(CREDITS)

@app.route("/vpa", methods=["GET", "POST"])
def number_to_vpa():
    init_session()
    if request.method == "GET":
        number = request.args.get("number")
    else:
        body = request.get_json(silent=True) or {}
        number = body.get("number") or body.get("upi_number")

    if not number:
        return jsonify({"error": "Missing 'number' parameter (query param or JSON body)"}), 400

    payload = {"upi_number": str(number)}

    try:
        resp = SESSION.post(HALFBLOOD_URL, json=payload, timeout=12)
    except requests.RequestException as e:
        return jsonify({"error": "Request to upstream failed", "details": str(e)}), 502

    try:
        upstream_json = resp.json()
    except ValueError:
        upstream_json = {"raw": resp.text}

    selected_credit = _pick_credit()

    if isinstance(upstream_json, dict):
        upstream_json["_credits"] = selected_credit
    else:
        upstream_json = {"result": upstream_json, "_credits": selected_credit}

    response = make_response(jsonify(upstream_json), resp.status_code if resp.status_code < 500 else 200)
    response.headers["X-Credits"] = selected_credit
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
