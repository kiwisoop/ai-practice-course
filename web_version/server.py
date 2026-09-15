"""Local web server for the browser digit-recognition application.

Created with Codex on 2026-09-10.
"""

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import sys
import webbrowser

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from mnist_model import load_or_train_model, predict_digit  # noqa: E402


ROUTES = {
    "/": (WEB_ROOT / "templates" / "index.html", "text/html; charset=utf-8"),
    "/app.js": (WEB_ROOT / "static" / "app.js", "text/javascript; charset=utf-8"),
    "/style.css": (WEB_ROOT / "static" / "style.css", "text/css; charset=utf-8"),
}


class DigitHandler(BaseHTTPRequestHandler):
    model = None

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        if route not in ROUTES:
            self.send_error(404)
            return
        path, content_type = ROUTES[route]
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(path.read_bytes())

    def do_POST(self) -> None:
        if self.path != "/predict":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 2_000_000:
                raise ValueError("Invalid image size.")
            payload = json.loads(self.rfile.read(length))
            encoded = payload["image"].split(",", 1)[1]
            image = Image.open(BytesIO(base64.b64decode(encoded, validate=True)))
            digit, confidence = predict_digit(self.model, image)
            self.send_json(200, {"digit": digit, "confidence": confidence})
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except Exception as error:
            print(f"Prediction error: {error}")
            self.send_json(500, {"error": "The image could not be recognized."})

    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string: str, *args) -> None:
        print(f"Web: {format_string % args}")


def main() -> None:
    DigitHandler.model = load_or_train_model()
    address = ("127.0.0.1", 8000)
    server = ThreadingHTTPServer(address, DigitHandler)
    url = "http://127.0.0.1:8000"
    print(f"Web application running at {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
