"use strict";

const $ = (id) => document.getElementById(id);
const isDiary = document.body.dataset.page === "diary";
const HISTORY_KEY = "study05.diary.v1";
const MOODS = ["맑음", "흐림", "기쁨", "지침"];
let activeRequest = false;

function status(message, error = false) {
  $("status").textContent = message;
  $("status").classList.toggle("error", error);
}

async function request(path, payload) {
  let response;
  try {
    response = await fetch(path, {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error("로컬 서버에 연결하지 못했습니다. 서버가 실행 중인지 확인해 주세요.");
  }
  let data;
  try { data = await response.json(); }
  catch { throw new Error("서버 응답을 읽지 못했습니다. 로컬 서버가 실행 중인지 확인해 주세요."); }
  if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : "요청을 처리하지 못했습니다. 다시 시도해 주세요.");
  return data;
}

function credentials() {
  const api_key = $("api-key").value.trim();
  const model = $("model").value;
  if (!api_key || !model) {
    document.querySelector(".connection").open = true;
    throw new Error("API 연결 설정에서 키를 입력하고 사용할 모델을 선택해 주세요.");
  }
  if (!$("consent").checked) throw new Error("내용 전송 안내를 확인하고 동의해 주세요.");
  return {api_key, model, consent: true};
}

function busy(value) {
  activeRequest = value;
  $("submit").disabled = value;
  $("load-models").disabled = value;
  document.querySelector("form").setAttribute("aria-busy", String(value));
}

$("api-key").addEventListener("input", () => {
  $("model").replaceChildren(new Option("먼저 모델을 불러오세요", ""));
});

$("load-models").addEventListener("click", async () => {
  if (activeRequest) return;
  const api_key = $("api-key").value.trim();
  if (!api_key) return status("학교 API 키를 입력해 주세요.", true);
  busy(true);
  status("사용 가능한 모델을 확인하고 있어요…");
  try {
    const data = await request("/api/models", {api_key});
    if (!Array.isArray(data.models) || !data.models.length || data.models.some((m) => typeof m !== "string" || !m)) throw new Error("사용 가능한 모델 목록이 올바르지 않습니다.");
    $("model").replaceChildren(new Option("모델을 선택하세요", ""), ...data.models.map((m) => new Option(m, m)));
    status("연결되었습니다. 사용할 모델을 선택해 주세요.");
  } catch (error) { status(error.message, true); }
  finally { busy(false); }
});

function validEntry(entry) {
  return entry && typeof entry === "object" && ["id", "date", "text", "emotion", "message"].every((key) => typeof entry[key] === "string") &&
    Number.isFinite(Date.parse(entry.date)) && entry.text.length <= 2000 && entry.emotion.length <= 60 && entry.message.length <= 3000 &&
    (entry.mood === undefined || entry.mood === "" || MOODS.includes(entry.mood));
}

function readHistory() {
  const raw = localStorage.getItem(HISTORY_KEY);
  if (raw === null) return [];
  const entries = JSON.parse(raw);
  if (!Array.isArray(entries) || !entries.every(validEntry)) throw new Error("저장된 기록 형식이 올바르지 않습니다.");
  return entries;
}

function renderHistory() {
  const root = $("history");
  root.replaceChildren();
  try {
    const entries = readHistory().sort((a, b) => Date.parse(b.date) - Date.parse(a.date));
    if (!entries.length) {
      const empty = document.createElement("p"); empty.className = "history-empty";
      empty.textContent = "아직 저장한 기록이 없어요. 첫 번째 하루를 남겨보세요.";
      root.append(empty);
    }
    for (const entry of entries) {
      const article = document.createElement("article"); article.className = "history-entry";
      const time = document.createElement("time"); time.dateTime = entry.date;
      time.textContent = new Date(entry.date).toLocaleDateString("ko-KR", {timeZone: "Asia/Seoul", year: "numeric", month: "long", day: "numeric"});
      const text = document.createElement("h3"); text.textContent = entry.text;
      const emotion = document.createElement("span"); emotion.className = "emotion"; emotion.textContent = entry.emotion;
      const message = document.createElement("p"); message.textContent = entry.message;
      if (entry.mood) {
        const mood = document.createElement("span"); mood.className = "record-mood"; mood.textContent = entry.mood;
        article.append(mood);
      }
      article.append(time, text, emotion, message); root.append(article);
    }
  } catch {
    $("history-status").textContent = "이 브라우저의 기록을 읽지 못했습니다. 기존 기록은 덮어쓰지 않습니다. 브라우저 저장 설정을 확인해 주세요.";
  }
}

if (isDiary) {
  $("diary-date").textContent = new Date().toLocaleDateString("ko-KR", {timeZone: "Asia/Seoul", year: "numeric", month: "long", day: "numeric", weekday: "long"});
  renderHistory();
  $("clear-history").addEventListener("click", () => {
    if (!confirm("이 브라우저에 저장된 일기와 답변을 모두 삭제할까요? 삭제하면 복구할 수 없습니다.")) return;
    try {
      localStorage.removeItem(HISTORY_KEY);
      $("history-status").textContent = "이 브라우저의 저장 기록을 삭제했습니다.";
      renderHistory();
    } catch { $("history-status").textContent = "기록을 삭제하지 못했습니다. 브라우저 저장 설정을 확인해 주세요."; }
  });
  $("diary-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (activeRequest) return;
    try {
      const payload = credentials();
      const text = $("diary-text").value.trim();
      if (!text || text.length > 2000) throw new Error("오늘 있었던 일을 1~2,000자로 적어 주세요.");
      const persist = $("persist").checked;
      const mood = document.querySelector('input[name="mood"]:checked')?.value || "";
      busy(true); status("키윗새가 당신의 이야기에 어울리는 답장을 준비하고 있어요…");
      const data = await request("/api/diary", {...payload, text, mood});
      if (typeof data.emotion !== "string" || !data.emotion.trim() || data.emotion.length > 60 || typeof data.message !== "string" || !data.message.trim() || data.message.length > 3000) throw new Error("분석 결과의 응답 형식이 올바르지 않습니다. 다시 시도해 주세요.");
      $("emotion").textContent = data.emotion; $("message").textContent = data.message;
      $("result").hidden = false; $("result-empty").hidden = true;
      status("키윗새의 답장이 도착했어요.");
      if (persist) {
        try {
          const entries = readHistory();
          entries.push({id: crypto.randomUUID(), date: new Date().toISOString(), text, mood, emotion: data.emotion, message: data.message});
          localStorage.setItem(HISTORY_KEY, JSON.stringify(entries));
          $("history-status").textContent = "이 브라우저에 기록을 저장했습니다.";
          renderHistory();
        } catch { $("history-status").textContent = "분석은 완료했지만 기록을 저장하지 못했습니다. 기존 기록은 유지됩니다. 브라우저 저장 설정과 여유 공간을 확인해 주세요."; }
      }
    } catch (error) { status(error.message, true); }
    finally { busy(false); }
  });
} else {
  $("pdf-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    if (activeRequest) return;
    try {
      const payload = credentials();
      const file = $("pdf-file").files[0];
      if (!file || !file.name.toLowerCase().endsWith(".pdf") || (file.type && file.type !== "application/pdf")) throw new Error("PDF 파일을 선택해 주세요.");
      if (!file.size || file.size > 10 * 1024 * 1024) throw new Error("PDF는 10MB 이하의 비어 있지 않은 파일이어야 합니다.");
      const mode = document.querySelector('input[name="mode"]:checked').value;
      busy(true); status("문서를 읽고 핵심을 정리하고 있어요…");
      const pdf = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(",", 2)[1]);
        reader.onerror = () => reject(new Error("파일을 읽지 못했습니다. PDF를 다시 선택해 주세요."));
        reader.readAsDataURL(file);
      });
      const data = await request("/api/pdf-summary", {...payload, pdf, mode});
      if (typeof data.summary !== "string" || !data.summary.trim() || !Number.isInteger(data.pages) || !Number.isInteger(data.characters)) throw new Error("요약 결과의 응답 형식이 올바르지 않습니다. 다시 시도해 주세요.");
      $("summary").textContent = data.summary;
      $("pdf-meta").textContent = `${file.name} · ${data.pages}쪽 · 텍스트 ${data.characters.toLocaleString("ko-KR")}자 · ${mode === "normal" ? "일반 요약" : "간단 요약"}`;
      $("result").hidden = false; $("result-empty").hidden = true;
      status("문서 요약이 준비되었습니다.");
    } catch (error) { status(error.message, true); }
    finally { busy(false); }
  });
}
