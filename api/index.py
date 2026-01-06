from flask import Flask, request, jsonify, make_response
import requests
import random
import os
import re

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

def is_phone_number(s):
    # Simple check for phone number (digits only, 10-12 chars)
    return s.isdigit() and 10 <= len(s) <= 12

@app.route('/contact', methods=['GET'])
def get_contact_info():
    init_session()
    number = request.args.get('number')
    if not number:
        return jsonify({"error": "Missing 'number' parameter"}), 400
    
    # If it's not a phone number, it might be a UPI ID. 
    # The /user/contact/in/ endpoint only works for phone numbers.
    if not is_phone_number(number):
        return jsonify({"error": "The /contact endpoint only supports phone numbers. For UPI IDs, use /vpa"}), 400

    url = f"{OFFICIAL_API_HOST}/user/contact/in/{number}/"
    try:
        response = SESSION.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

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

    # If it's a phone number, try to get contact info first
    if is_phone_number(number):
        contact_url = f"{OFFICIAL_API_HOST}/user/contact/in/{number}/"
        try:
            contact_resp = SESSION.get(contact_url, timeout=10)
            contact_resp.raise_for_status()
            contact_data = contact_resp.json()
            
            payload = {"upi_number": str(number)}
            vpa_resp = SESSION.post(HALFBLOOD_URL, json=payload, timeout=12)
            vpa_data = vpa_resp.json() if vpa_resp.status_code == 200 else {}
            
            combined_data = {
                "contact_info": contact_data,
                "vpa_info": vpa_data,
                "_credits": _pick_credit()
            }
            return jsonify(combined_data)
        except Exception as e:
            # Fallback to just VPA
            pass

    # For UPI IDs or if contact lookup failed
    payload = {"upi_number": str(number)}
    try:
        vpa_resp = SESSION.post(HALFBLOOD_URL, json=payload, timeout=12)
        vpa_resp.raise_for_status()
        vpa_data = vpa_resp.json()
        vpa_data["_credits"] = _pick_credit()
        return jsonify(vpa_data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e), "message": "Failed to retrieve VPA info"}), 500

@app.route('/')
def index():
    return "Fampa API is running. Use /contact?number=... or /vpa?number=..."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
