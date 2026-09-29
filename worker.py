import time
from app.database import init_db, save_event, save_alert
from app.queue import pop_event
from app.security import SecurityDetector

init_db()
detector = SecurityDetector(threshold=3)
print("Security worker started")

while True:
    event = pop_event(timeout=2)
    if not event:
        continue
    save_event(event)
    alert = detector.process(event)
    if alert:
        save_alert(alert)
        print(f"ALERT: {alert}")
