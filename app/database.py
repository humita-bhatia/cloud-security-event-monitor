import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("DB_PATH", "/data/security.db")


@contextmanager
def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server TEXT NOT NULL,
            event_type TEXT NOT NULL,
            ip TEXT,
            timestamp TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )""")


def save_event(event):
    with get_db() as db:
        db.execute(
            "INSERT INTO events(server,event_type,ip,timestamp) VALUES(?,?,?,?)",
            (event["server"], event["event_type"], event.get("ip"), event["timestamp"]),
        )


def save_alert(alert):
    with get_db() as db:
        columns = {row[1] for row in db.execute("PRAGMA table_info(alerts)").fetchall()}
        if "severity" in columns:
            # Compatibility with an older local database created before severity
            # was removed from the dashboard. New databases do not use it.
            db.execute(
                "INSERT INTO alerts(server,alert_type,reason,severity,timestamp) VALUES(?,?,?,?,?)",
                (alert["server"], alert["alert_type"], alert["reason"], "ALERT", alert["timestamp"]),
            )
        else:
            db.execute(
                "INSERT INTO alerts(server,alert_type,reason,timestamp) VALUES(?,?,?,?)",
                (alert["server"], alert["alert_type"], alert["reason"], alert["timestamp"]),
            )


def recent_events(limit=25):
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


def recent_alerts(limit=25):
    with get_db() as db:
        return [dict(r) for r in db.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]


def counts():
    with get_db() as db:
        events = db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        alerts = db.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        servers = db.execute("SELECT COUNT(DISTINCT server) FROM events").fetchone()[0]
        return {"events": events, "alerts": alerts, "servers": servers, "servers_monitored": 3}
