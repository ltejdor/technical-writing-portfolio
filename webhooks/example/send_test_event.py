"""Send a signed test event to the local receiver, the way Relay would.

Usage:
  python3 send_test_event.py              # a valid event
  python3 send_test_event.py --duplicate  # the same event twice
  python3 send_test_event.py --tampered   # body changed after signing
  python3 send_test_event.py --expired    # signed 10 minutes ago
"""

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

URL = "http://localhost:8000/webhooks/relay"
SIGNING_SECRET = os.environ.get("RELAY_SIGNING_SECRET", "whsec_test_secret")


def build_event():
    return {
        "id": f"evt_{uuid.uuid4().hex[:12]}",
        "type": "notification.delivered",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "data": {
            "id": "ntf_01HZX3K8D2",
            "customer_id": "cus_7Q2M9X",
            "notification_type": "otp",
            "category": "mandatory",
            "reference": "login-2026-10-22-0042",
            "status": "delivered",
            "attempt": {"channel": "sms", "status": "delivered", "reason": None},
        },
    }


def sign(body, timestamp):
    signed_payload = str(timestamp).encode() + b"." + body
    signature = hmac.new(SIGNING_SECRET.encode(), signed_payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def send(body, signature_header):
    request = urllib.request.Request(
        URL,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", "Relay-Signature": signature_header},
    )
    try:
        with urllib.request.urlopen(request) as response:
            print(f"Receiver answered {response.status}")
    except urllib.error.HTTPError as error:
        print(f"Receiver answered {error.code}")
    except urllib.error.URLError:
        print("Couldn't connect. Is receiver.py running?")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    body = json.dumps(build_event()).encode()
    timestamp = int(time.time())

    if mode == "--expired":
        timestamp -= 10 * 60
    header = sign(body, timestamp)

    if mode == "--tampered":
        body = body.replace(b'"delivered"', b'"not_delivered"', 1)

    send(body, header)
    if mode == "--duplicate":
        send(body, header)
