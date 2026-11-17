"""14주차 실습 서버. 내 컴퓨터에서만 실행하고 입력·키는 기록하지 않는다."""

import base64
import binascii
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

import ai

ROOT = Path(__file__).resolve().parent
PORT = 8514
ORIGIN = f"http://127.0.0.1:{PORT}"
MAX_BODY = 14 * 1024 * 1024
FILES = {"/": ("index.html", "text/html"), "/index.html": ("index.html", "text/html"),
         "/index_pdf.html": ("index_pdf.html", "text/html"),
         "/style.css": ("style.css", "text/css"), "/app.js": ("app.js", "text/javascript"),
         "/assets/kiwi-friend.png": ("assets/kiwi-friend.png", "image/png")}
FILES["/diary.css"] = ("diary.css", "text/css")
FILES["/assets/paper.svg"] = ("assets/paper.svg", "image/svg+xml")
FILES["/assets/fonts/MaruBuri-Regular.woff2"] = ("assets/fonts/MaruBuri-Regular.woff2", "font/woff2")
FILES["/assets/fonts/MaruBuri-SemiBold.woff2"] = ("assets/fonts/MaruBuri-SemiBold.woff2", "font/woff2")


def dispatch(path, data):
    if not isinstance(data, dict):
        raise ValueError("요청 형식이 올바르지 않습니다.")
    key, model = data.get("api_key"), data.get("model")
    if not isinstance(key, str):
        raise ValueError("API 키를 입력해 주세요.")
    if path == "/api/models":
        return {"models": ai.list_models(key)}
    if data.get("consent") is not True:
        raise ValueError("전송 안내를 확인하고 동의해 주세요.")
    if not isinstance(model, str) or not model.strip() or len(model) > 200:
        raise ValueError("사용할 모델을 선택해 주세요.")
    if path == "/api/diary":
        text = data.get("text")
        if not isinstance(text, str):
            raise ValueError("일기를 입력해 주세요.")
        mood = data.get("mood", "")
        if not isinstance(mood, str) or mood not in ("", "맑음", "흐림", "기쁨", "지침"):
            raise ValueError("오늘의 마음을 목록에서 선택해 주세요.")
        return ai.analyze_diary(key, model, text, mood=mood)
    if path == "/api/pdf-summary":
        encoded = data.get("pdf")
        if not isinstance(encoded, str):
            raise ValueError("PDF 파일을 선택해 주세요.")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise ValueError("PDF 파일 데이터를 읽지 못했습니다.") from None
        return ai.summarize_pdf(key, model, raw, data.get("mode"))
    raise ValueError("지원하지 않는 요청입니다.")


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, format, *args):
        # 일기·키·파일명 등 요청 내용을 로그에 남기지 않는다.
        pass

    def reply(self, status, body, content_type="application/json"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def allowed_host(self):
        return self.headers.get("Host") == f"127.0.0.1:{PORT}"

    def do_GET(self):
        if not self.allowed_host():
            self.reply(403, {"error": "로컬 앱 주소로 접속해 주세요."})
            return
        resource = FILES.get(self.path)
        if resource is None:
            self.reply(404, {"error": "페이지를 찾을 수 없습니다."})
            return
        name, mime = resource
        try:
            self.reply(200, (ROOT / name).read_bytes(), mime)
        except OSError:
            self.reply(500, {"error": "앱 파일을 읽지 못했습니다."})

    def do_POST(self):
        if not self.allowed_host() or self.headers.get("Origin") != ORIGIN:
            self.reply(403, {"error": "앱 화면에서 요청해 주세요."})
            return
        if self.path not in {"/api/models", "/api/diary", "/api/pdf-summary"}:
            self.reply(404, {"error": "지원하지 않는 요청입니다."})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/json":
            self.reply(415, {"error": "JSON 형식으로 요청해 주세요."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= MAX_BODY:
                self.reply(413, {"error": "요청이 비었거나 너무 큽니다. PDF는 10MB 이하로 선택해 주세요."})
                return
            data = json.loads(self.rfile.read(length))
            self.reply(200, dispatch(self.path, data))
        except (ValueError, UnicodeError) as error:
            message = "요청 내용을 읽지 못했습니다." if isinstance(error, (json.JSONDecodeError, UnicodeError)) else str(error)
            self.reply(400, {"error": message})
        except Exception:
            self.reply(500, {"error": "처리 중 오류가 발생했습니다. 입력을 확인하고 다시 시도해 주세요."})


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as server:
        print(f"14주차 실습: {ORIGIN}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
