#!/usr/bin/env python3
"""Study-06 shopping-list.html automated browser verification using Playwright MCP."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

STUDY_DIR = pathlib.Path(__file__).resolve().parent
HTML_PATH = STUDY_DIR / "shopping-list.html"
SCREENSHOT_DIR = STUDY_DIR / "screenshots"


class PlaywrightMCPClient:
    def __init__(self, temp_output_dir: pathlib.Path):
        self.proc = subprocess.Popen(
            [
                "npx",
                "-y",
                "@playwright/mcp@latest",
                "--headless",
                "--isolated",
                "--allow-unrestricted-file-access",
                "--viewport-size",
                "960x760",
                "--output-dir",
                str(temp_output_dir),
            ],
            cwd=str(STUDY_DIR),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self.req_id = 0

    def request(self, method: str, params: dict) -> dict:
        self.req_id += 1
        current_id = self.req_id
        payload = {"jsonrpc": "2.0", "id": current_id, "method": method, "params": params}
        assert self.proc.stdin is not None
        assert self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

        while True:
            line = self.proc.stdout.readline()
            if not line:
                err = self.proc.stderr.read() if self.proc.stderr else ""
                raise RuntimeError(f"Playwright MCP terminated unexpectedly: {err}")
            msg = json.loads(line)
            if msg.get("id") == current_id:
                if "error" in msg:
                    raise RuntimeError(f"MCP error: {msg['error']}")
                return msg["result"]

    def notify(self, method: str, params: dict | None = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(payload) + "\n")
        self.proc.stdin.flush()

    def call_tool(self, name: str, arguments: dict) -> str:
        res = self.request("tools/call", {"name": name, "arguments": arguments})
        if res.get("isError"):
            raise RuntimeError(f"Tool {name} failed: {res}")
        texts = [c.get("text", "") for c in res.get("content", []) if c.get("type") == "text"]
        return "\n".join(texts)

    def eval_state(self) -> dict:
        fn = """() => {
          const items = Array.from(document.querySelectorAll('#shopping-list .shopping-item')).map(li => ({
            name: li.querySelector('.item-name').textContent,
            completed: li.classList.contains('is-completed'),
            checked: li.querySelector('.item-checkbox').checked,
            hasScriptChild: Boolean(li.querySelector('script, img, b'))
          }));
          return {
            items,
            total: document.getElementById('total-count').textContent,
            completed: document.getElementById('completed-count').textContent,
            remaining: document.getElementById('remaining-count').textContent,
            status: document.getElementById('status-message').textContent,
            isError: document.getElementById('status-message').classList.contains('is-error'),
            emptyHidden: document.getElementById('empty-state').hidden,
            rawStorage: window.localStorage.getItem('study06.shoppingList.v1')
          };
        }"""
        out = self.call_tool("browser_evaluate", {"function": fn})
        marker = "### Result\n"
        if marker in out:
            rest = out.split(marker, 1)[1]
            json_block = rest.split("\n### ", 1)[0].strip()
            return json.loads(json_block)
        raise RuntimeError(f"Could not parse browser_evaluate output:\n{out}")

    def close(self) -> None:
        try:
            self.call_tool("browser_close", {})
        except Exception:
            pass
        self.proc.terminate()
        self.proc.wait(timeout=5)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"[{label}] expected {expected!r}, got {actual!r}")


def run_tests() -> None:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="study06-pw-mcp-"))
    client = PlaywrightMCPClient(temp_dir)

    try:
        init_info = client.request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "study06-verifier", "version": "1.0.0"},
            },
        )
        client.notify("notifications/initialized")
        print(f"Connected to MCP server: {init_info.get('serverInfo')}")

        url = HTML_PATH.as_uri()
        client.call_tool("browser_navigate", {"url": url})
        client.call_tool("browser_evaluate", {"function": "() => { localStorage.clear(); location.reload(); }"})

        # 1. Empty input rejection
        client.call_tool("browser_type", {"element": "쇼핑 아이템 입력창", "target": "#item-input", "text": "   ", "submit": True})
        state = client.eval_state()
        assert_equal(state["total"], "0", "빈 입력 후 전체 개수")
        assert_equal(state["isError"], True, "빈 입력 오류 표시")
        assert_equal(state["emptyHidden"], False, "빈 목록 안내 표시")
        print("[PASS] 1. 빈 입력 거부 확인")

        # 2. Add 사과, 우유, 빵 (via Enter submit and button click)
        client.call_tool("browser_type", {"element": "사과 입력", "target": "#item-input", "text": "사과", "submit": True})
        client.call_tool("browser_type", {"element": "우유 입력", "target": "#item-input", "text": "우유", "submit": False})
        client.call_tool("browser_click", {"element": "추가 버튼", "target": "#add-button"})
        client.call_tool("browser_type", {"element": "빵 입력", "target": "#item-input", "text": "빵", "submit": True})

        state = client.eval_state()
        assert_equal([i["name"] for i in state["items"]], ["사과", "우유", "빵"], "사과·우유·빵 추가 목록")
        assert_equal((state["total"], state["completed"], state["remaining"]), ("3", "0", "3"), "추가 후 요약 수치")
        client.call_tool("browser_take_screenshot", {"filename": "screenshots/01-added-items.png"})
        print("[PASS] 2. 사과·우유·빵 추가 및 요약 확인")

        # 3. Check 사과 & 우유 -> completed state, then uncheck 사과 -> restore state
        client.call_tool("browser_click", {"element": "사과 구매 완료 체크박스", "target": 'input[aria-label="사과 구매 완료"]'})
        client.call_tool("browser_click", {"element": "우유 구매 완료 체크박스", "target": 'input[aria-label="우유 구매 완료"]'})
        state = client.eval_state()
        assert_equal([i["completed"] for i in state["items"]], [True, True, False], "사과·우유 체크 완료 표시")
        assert_equal((state["total"], state["completed"], state["remaining"]), ("3", "2", "1"), "체크 후 요약 수치")
        client.call_tool("browser_take_screenshot", {"filename": "screenshots/02-checked-items.png"})

        client.call_tool("browser_click", {"element": "사과 체크 해제", "target": 'input[aria-label="사과 구매 완료"]'})
        state = client.eval_state()
        assert_equal([i["completed"] for i in state["items"]], [False, True, False], "사과 체크 해제 후 원상 복구")
        assert_equal((state["total"], state["completed"], state["remaining"]), ("3", "1", "2"), "체크 해제 후 요약 수치")
        print("[PASS] 3. 구매 체크 시 완료 표시 및 해제 시 원상 복구 확인")

        # 4. Delete 우유 & 빵 -> only target items removed, 사과 remains
        client.call_tool("browser_click", {"element": "우유 삭제 버튼", "target": 'button[aria-label="우유 삭제"]'})
        state = client.eval_state()
        assert_equal([i["name"] for i in state["items"]], ["사과", "빵"], "우유 삭제 후 남은 목록")

        client.call_tool("browser_click", {"element": "빵 삭제 버튼", "target": 'button[aria-label="빵 삭제"]'})
        state = client.eval_state()
        assert_equal([i["name"] for i in state["items"]], ["사과"], "빵 삭제 후 남은 목록")
        assert_equal((state["total"], state["completed"], state["remaining"]), ("1", "0", "1"), "삭제 후 요약 수치")
        client.call_tool("browser_take_screenshot", {"filename": "screenshots/03-after-delete.png"})
        print("[PASS] 4. 삭제 시 해당 상품만 제거 확인")

        # 5. Reload persistence & safe text rendering (XSS guard)
        xss_text = "<img src=x onerror=alert(1)>치즈"
        client.call_tool("browser_type", {"element": "특수문자 상품 입력", "target": "#item-input", "text": xss_text, "submit": True})
        client.call_tool("browser_click", {"element": "특수문자 상품 체크", "target": f'input[aria-label="{xss_text} 구매 완료"]'})
        client.call_tool("browser_evaluate", {"function": "() => { location.reload(); }"})
        state = client.eval_state()
        assert_equal([i["name"] for i in state["items"]], ["사과", xss_text], "새로고침 후 목록 복원 및 안전한 텍스트 표시")
        assert_equal([i["completed"] for i in state["items"]], [False, True], "새로고침 후 완료 상태 복원")
        assert_equal(any(i["hasScriptChild"] for i in state["items"]), False, "HTML 태그 미실행 확인")
        print("[PASS] 5. 새로고침 후 복원 및 안전한 텍스트 표시 확인")

        # 6. Storage failure & corrupted JSON recovery
        storage_test = client.call_tool(
            "browser_evaluate",
            {
                "function": """() => {
                  const origSetItem = Storage.prototype.setItem;
                  Storage.prototype.setItem = function() { throw new Error('QuotaExceededError'); };
                  const input = document.getElementById('item-input');
                  input.value = '토마토';
                  document.getElementById('shopping-form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                  const afterFailItems = Array.from(document.querySelectorAll('#shopping-list .item-name')).map(el => el.textContent);
                  const afterFailError = document.getElementById('status-message').classList.contains('is-error');
                  const afterFailMsg = document.getElementById('status-message').textContent;
                  Storage.prototype.setItem = origSetItem;
                  return { afterFailItems, afterFailError, afterFailMsg };
                }"""
            },
        )
        assert "토마토" in storage_test and "true" in storage_test, f"Storage failure test unexpected output: {storage_test}"

        # Restore clean final state for final screenshot (사과, 우유(완료), 빵)
        client.call_tool(
            "browser_evaluate",
            {
                "function": """() => {
                  localStorage.setItem('study06.shoppingList.v1', JSON.stringify([
                    { id: 'item-1', name: '사과', completed: false },
                    { id: 'item-2', name: '우유', completed: true },
                    { id: 'item-3', name: '빵', completed: false }
                  ]));
                  location.reload();
                }"""
            },
        )
        client.call_tool("browser_take_screenshot", {"filename": "screenshots/shopping-list-test.png"})

        # Also test corrupted storage load recovery
        client.call_tool(
            "browser_evaluate",
            {
                "function": """() => {
                  localStorage.setItem('study06.shoppingList.v1', '{broken-json');
                  location.reload();
                }"""
            },
        )
        corrupted_state = client.eval_state()
        assert_equal(corrupted_state["total"], "0", "손상된 저장소 복구 시 빈 목록 시작")
        assert_equal(corrupted_state["isError"], True, "손상된 저장소 안내 표시")
        print("[PASS] 6. 저장 실패 및 손상된 저장 데이터 복구 확인")

        print("\nAll Playwright MCP checks passed successfully.")
    finally:
        client.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
        pw_mcp_dir = STUDY_DIR / ".playwright-mcp"
        if pw_mcp_dir.exists():
            shutil.rmtree(pw_mcp_dir, ignore_errors=True)


if __name__ == "__main__":
    try:
        run_tests()
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        sys.exit(1)
