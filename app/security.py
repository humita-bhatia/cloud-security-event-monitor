from collections import deque
from datetime import datetime, timezone


class SecurityDetector:
    def __init__(self, threshold=3):
        self.threshold = threshold
        self.failed_logins = {}

    def process(self, event):
        if event["event_type"] != "LOGIN_FAILURE":
            return None

        key = (event["server"], event.get("ip") or "unknown")
        attempts = self.failed_logins.setdefault(key, deque(maxlen=self.threshold))
        attempts.append(event["timestamp"])

        if len(attempts) == self.threshold:
            alert = {
                "server": event["server"],
                "alert_type": "POSSIBLE_BRUTE_FORCE",
                "reason": f"{self.threshold} failed logins detected for {key[1]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            # Start a new burst after an alert so one continuous burst
            # produces one alert instead of repeated alerts.
            attempts.clear()
            return alert

        return None
