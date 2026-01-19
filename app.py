from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests.auth import HTTPDigestAuth
import traceback
import logging

# ================== CONFIG ==================
APP_PORT = 9000
REQUEST_TIMEOUT = 6
# ============================================

# TẠO APP (BẮT BUỘC PHẢI Ở TRÊN)
app = Flask(__name__)

# BẬT CORS
CORS(app)

# LOG RA TERMINAL
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def log(msg):
    logging.info(msg)

# ================== CORE HIK REQUEST ==================
def hik_request(host, user, pwd, path, method="GET", body=None):
    url = f"http://{host}{path}"
    log(f"HIK {method} {url}")

    try:
        r = requests.request(
            method=method,
            url=url,
            auth=HTTPDigestAuth(user, pwd),
            data=body,
            headers={"Content-Type": "application/xml"},
            timeout=REQUEST_TIMEOUT
        )
        log(f"→ STATUS {r.status_code}")
        return r.status_code, r.text

    except Exception as e:
        log("❌ REQUEST ERROR")
        traceback.print_exc()
        return 0, str(e)

# ================== API ==================

@app.route("/")
def health():
    return "Hikvision API Server running OK"

@app.route("/api/test", methods=["POST"])
def api_test():
    data = request.json or {}
    code, text = hik_request(
        data.get("host"),
        data.get("user"),
        data.get("pass"),
        "/ISAPI/System/deviceInfo"
    )
    return jsonify({
        "ok": code == 200,
        "status": code,
        "raw": text[:300]
    })

@app.route("/api/users", methods=["POST"])
def api_users():
    data = request.json or {}
    code, text = hik_request(
        data.get("host"),
        data.get("user"),
        data.get("pass"),
        "/ISAPI/Security/users"
    )
    return jsonify({
        "ok": code == 200,
        "status": code,
        "xml": text
    })

@app.route("/api/change", methods=["POST"])
def api_change():
    data = request.json or {}

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<User>
  <id>{data.get("id")}</id>
  <userName>{data.get("name")}</userName>
  <password>{data.get("newpass")}</password>
</User>"""

    code, text = hik_request(
        data.get("host"),
        data.get("user"),
        data.get("pass"),
        f"/ISAPI/Security/users/{data.get('id')}",
        method="PUT",
        body=xml
    )

    return jsonify({
        "ok": code == 200,
        "status": code,
        "raw": text[:300]
    })

# ================== MAIN ==================
if __name__ == "__main__":
    print("========================================")
    print(" Hikvision ISAPI Python Backend ")
    print(f" Running on port {APP_PORT}")
    print("========================================")

    app.run(
        host="0.0.0.0",
        port=APP_PORT,
        debug=True
    )
