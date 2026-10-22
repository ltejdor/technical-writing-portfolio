"""Minimal Relay webhook receiver, for learning and local testing.

Run it with:  python3 receiver.py
It listens on http://localhost:8000/webhooks/relay

It shows the three things every receiver must do:
  1. Verify the signature, so you only accept events Relay sent.
  2. Ignore events you've already processed (Relay may send one twice).
  3. Answer 2xx quickly, then do the slow work.

Not production code: processed event IDs are kept in memory and lost on restart.
In production, store them in a database.
"""

import hashlib
import hmac
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# The signing secret from your Relay configuration. Never hard-code it in real code.
SIGNING_SECRET = os.environ.get("RELAY_SIGNING_SECRET", "whsec_test_secret")

# Reject events signed more than 5 minutes ago, to block replayed requests.
TOLERANCE_SECONDS = 5 * 60

PATH = "/webhooks/relay"
processed_event_ids = set()


def verify_signature(header, body, secret, now=None):
    """Return True if the Relay-Signature header matches the body."""
    if not header:
        return False
    parts = dict(item.split("=", 1) for item in header.split(",") if "=" in item)
    timestamp, signature = parts.get("t"), parts.get("v1")
    if not timestamp or not signature or not timestamp.isdigit():
        return False

    now = int(now if now is not None else time.time())
    if abs(now - int(timestamp)) > TOLERANCE_SECONDS:
        return False

    signed_payload = timestamp.encode() + b"." + body
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    # compare_digest takes the same time whether the strings match or not.
    return hmac.compare_digest(expected, signature)


def handle_event(event):
    """Your business logic goes here. Keep it fast, or hand it to a queue."""
    data = event["data"]
    print(
        f"  -> {event['type']}: notification {data['id']} "
        f"for {data['customer_id']} is now '{data['status']}'"
    )


class RelayWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != PATH:
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        # Read the raw bytes: the signature is calculated on them, not on parsed JSON.
        body = self.rfile.read(length)

        if not verify_signature(self.headers.get("Relay-Signature"), body, SIGNING_SECRET):
            print("Rejected: invalid or expired signature")
            self.send_response(400)
            self.end_headers()
            return

        event = json.loads(body)

        if event["id"] in processed_event_ids:
            # Already handled. Answer 200 so Relay stops retrying.
            print(f"Duplicate {event['id']}: ignored")
            self.send_response(200)
            self.end_headers()
            return

        print(f"Accepted {event['id']}")
        handle_event(event)
        processed_event_ids.add(event["id"])

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # Keep the terminal output readable.


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), RelayWebhookHandler)
    print(f"Listening on http://localhost:8000{PATH}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
