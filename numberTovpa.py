# app.py
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Endpoint from PHP code
HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"

# Preserving the original auth token
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "eyJlbmMiOiJBMjU2Q0JDLUhTNTEyIiwiZXBrIjp7Imt0eSI6Ik9LUCIsImNydiI6Ilg0NDgiLCJ4IjoidDQta3N4bE9pQmQ5d0VCWTRza3BmQVNkM1J3RHYyUWI1U3B2cmJEbWVVWWtubHBnWWtlWFEtU3FVWkVITzZBcGVqTnJ6SGxPOUdvIn0sImFsZyI6IkVDREgtRVMifQ..4zww34voRaVXMOqJjnBJtg.6g_QjERM9tuKNwJN-lnbnLr811XrVl6veOMx0wvyimvcF16TNBGjSabGiZJsDTwX0ZiHXVyWGuanjkaPKEjDQCHiZ4J97WKHK4lPpMlUTAV4RRzw4kNI5ZPOnMJ7DOQJlFtsOCobnF9Rv8JKoQKkHl7PDphDy16kOWpaov-zQ-76eY8ONplYNkZbG0sOYjlzK68-9gZa5V3dwQjf67f7jNwhhS3KZrLtf0gSPlxS7URynCbOOa75eKNgAXrTOXaEgUPO2w_pr8xQgrfB-Rto3ObMvb7y_DE99C06mS7MUktzLDW8agLhBDM-ti1m65H9K-De41iiCtv-PH1z9_g-xbwlWnaQDPKYITFYiryUpzcEfLBG4zYcA4Va8a82_yt-.zaENNo7SpZQXnuHoYPUahrqJblvnViVbaqulutcAiwY")
USER_AGENT = "A015 | Android 15 | Dalvik/2.1.0"

SESSION = None

def init_session():
    global SESSION
    if SESSION is None:
        SESSION = requests.Session()
        SESSION.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "authorization": f"Token {AUTH_TOKEN}"
        })

def is_phone_number(s):
    return s.isdigit() and 10 <= len(s) <= 12

@app.route("/vpa", methods=["GET", "POST"])
def number_to_vpa():
    init_session()
    if request.method == "GET":
        number = request.args.get("number")
    else:
        body = request.get_json(silent=True) or {}
        number = body.get("number") or body.get("upi_number")

    if not number:
        return jsonify({"error": "Missing 'number' parameter"}), 400

    upi_id = number
    if is_phone_number(number) and "@" not in number:
        upi_id = f"{number}@fam"

    payload = {"upi_string": f"upi://pay?pa={upi_id}"}

    try:
        resp = SESSION.post(HALFBLOOD_URL, json=payload, timeout=12)
        resp.raise_for_status()
        data = resp.json()
        
        # Extracting only the phone number from the response
        # Based on the JSON structure provided by the user earlier
        phone_number = data.get("data", {}).get("verify_vpa_resp", {}).get("user", {}).get("contact", {}).get("phone_number")
        
        if not phone_number:
            # Fallback check in case the structure is slightly different
            phone_number = data.get("user", {}).get("contact", {}).get("phone_number")

        return jsonify({"phone_number": phone_number})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
