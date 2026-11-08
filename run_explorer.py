"""## Interactive run explorer

Run `python run_explorer.py` to open the local browser app. It reads runs with GPS
streams from `my_data` using the existing loader. Choose a broad area to zoom in,
filter by date, switch between routes and a density-style heat view, and select a
route or list entry for its distance and elapsed-time pace. Drag to pan and scroll
to zoom. Export PNG saves the current map view, including any selected route.
The map has no basemap and sends no location data to a mapping service. Area groups
are approximate, and the heat view is a visual density rendering rather than the
velocity-weighted histogram in `heatmap.py`. Press Ctrl+C in the terminal to stop."""

import datetime
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import strava_shared


def activity_data(activity):
    if (
        not activity.activity_type.is_run
        or not activity.latlng
        or not activity.distance
    ):
        return None
    points = [point for point in activity.latlng if point and len(point) == 2]
    if not points:
        return None
    duration = None
    if activity.time and len(activity.time) > 1:
        elapsed = activity.time[-1] - activity.time[0]
        duration = (
            elapsed.total_seconds()
            if isinstance(elapsed, datetime.timedelta)
            else elapsed
        )
    return {
        "id": activity.activity_id,
        "date": activity.date.isoformat() if activity.date else None,
        "distance": activity.distance[-1],
        "duration": duration,
        "points": points,
    }


def main():
    activities = [
        data
        for activity in strava_shared.load_activities(require_cadences=False)
        if (data := activity_data(activity)) is not None
    ]
    payload = json.dumps(activities, allow_nan=False).encode()
    page = (Path(__file__).parent / "run_explorer.html").read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                content, kind = page, "text/html; charset=utf-8"
            elif self.path == "/data":
                content, kind = payload, "application/json"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"Run explorer: {url} (Ctrl+C to stop)")
    threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
