from app.security import SecurityDetector


def event(event_type="LOGIN_FAILURE", server="Server-01", ip="10.0.0.1"):
    return {"event_type": event_type, "server": server, "ip": ip, "timestamp": "2026-09-29T10:00:00+00:00"}


def test_non_login_event_does_not_alert():
    detector = SecurityDetector()
    assert detector.process(event("FILE_ACCESS")) is None


def test_first_failed_login_does_not_alert():
    detector = SecurityDetector()
    assert detector.process(event()) is None


def test_third_failed_login_creates_alert():
    detector = SecurityDetector()
    detector.process(event())
    detector.process(event())
    alert = detector.process(event())
    assert alert is not None
    assert alert["alert_type"] == "POSSIBLE_BRUTE_FORCE"


def test_different_ips_are_tracked_separately():
    detector = SecurityDetector()
    detector.process(event(ip="10.0.0.1"))
    detector.process(event(ip="10.0.0.2"))
    detector.process(event(ip="10.0.0.1"))
    assert detector.process(event(ip="10.0.0.2")) is None


def test_alert_is_not_repeated_for_same_burst():
    detector = SecurityDetector()
    detector.process(event())
    detector.process(event())
    assert detector.process(event()) is not None
    assert detector.process(event()) is None

