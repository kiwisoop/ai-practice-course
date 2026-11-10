"use strict";

const { questions, categories } = globalThis.QUIZ_DATA;
const game = { started: false, index: 0, answers: [], completedAt: null, saved: false, mode: "normal", questions, hints: [], deadline: null };
const RECORD_KEY = "study03.records.v1";

function dailyQuestions(date = new Date().toLocaleDateString("sv-SE")) {
  let seed = [...date].reduce((value, ch) => (value * 31 + ch.charCodeAt(0)) >>> 0, 1);
  const pool = [...questions, ...(globalThis.QUIZ_DATA.extraQuestions || [])];
  for (let i = pool.length - 1; i > 0; i--) {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    const j = seed % (i + 1);
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, 10);
}
function startGame(mode = "normal", category = categories[0], now = Date.now()) {
  if (!["normal", "speed", "practice", "daily"].includes(mode) || !categories.includes(category)) throw new Error("잘못된 게임 설정");
  game.mode = mode;
  game.questions = mode === "daily" ? dailyQuestions() : mode === "practice" ? questions.filter(q => q.category === category) : questions;
  game.hints = [];
  game.deadline = mode === "speed" ? now + 15000 : null;
  game.started = true;
  game.index = 0;
  game.answers = [];
  game.completedAt = null;
  game.saved = false;
}

function answer(choice, now = Date.now()) {
  if (expireQuestion(now)) return false;
  if (!game.started || game.index >= game.questions.length || game.answers[game.index] !== undefined ||
      !Number.isInteger(choice) || choice < 0 || choice >= 4) return false;
  game.answers[game.index] = choice;
  return true;
}

function expireQuestion(now = Date.now()) {
  if (game.started && game.mode === "speed" && game.index < game.questions.length && game.answers[game.index] === undefined && now >= game.deadline) {
    game.answers[game.index] = -1;
    return true;
  }
  return false;
}
function useHint() {
  if (!game.started || game.mode === "normal" || game.index >= game.questions.length || game.answers[game.index] !== undefined || game.hints.includes(game.index)) return false;
  game.hints.push(game.index);
  return true;
}

function nextQuestion() {
  if (!game.started || game.index >= game.questions.length || game.answers[game.index] === undefined) return false;
  game.index += 1;
  game.deadline = game.mode === "speed" ? Date.now() + 15000 : null;
  if (game.index === game.questions.length) game.completedAt = new Date().toISOString();
  return true;
}

function scores() {
  const byCategory = Object.fromEntries(categories.map(category => [category, 0]));
  game.answers.forEach((choice, index) => {
    if (choice === game.questions[index].answer_index) byCategory[game.questions[index].category] += 1;
  });
  const total = Object.values(byCategory).reduce((sum, score) => sum + score, 0);
  const points = game.answers.reduce((sum, choice, index) => sum + (choice === game.questions[index].answer_index ? (game.mode === "speed" ? 10 - (game.hints.includes(index) ? 2 : 0) : 1) : 0), 0);
  return { byCategory, total, points };
}

function validName(name) {
  return typeof name === "string" && name.trim().length >= 1 && name.trim().length <= 20;
}

function recordKey(mode) { return mode === "normal" ? RECORD_KEY : `study03.records.${mode}.v1`; }
function readRecords(storage, mode = game.mode) {
  const raw = storage.getItem(recordKey(mode));
  const records = raw === null ? [] : JSON.parse(raw);
  if (!Array.isArray(records) || !records.every(record => {
    if (!record || !validName(record.name) || record.name !== record.name.trim() ||
        !Number.isInteger(record.total) || record.total < 0 || record.total > (record.questionCount || 50) ||
        typeof record.completedAt !== "string" || !Number.isFinite(Date.parse(record.completedAt)) ||
        new Date(record.completedAt).toISOString() !== record.completedAt ||
        !record.byCategory || typeof record.byCategory !== "object" ||
        (record.points !== undefined && (!Number.isInteger(record.points) || (mode === "speed" ? record.points < record.total * 8 || record.points > record.total * 10 || record.points % 2 !== 0 : record.points !== record.total))) ||
        (mode !== "normal" && (record.mode !== mode || record.questionCount !== (mode === "speed" ? 50 : 10) || !Number.isInteger(record.points))) ||
        (mode === "normal" && ((record.questionCount !== undefined && record.questionCount !== 50) || (record.mode !== undefined && record.mode !== "normal")))) return false;
    const values = categories.map(category => record.byCategory[category]);
    return Object.keys(record.byCategory).length === categories.length &&
      values.every(value => Number.isInteger(value) && value >= 0 && value <= 10) &&
      values.reduce((sum, value) => sum + value, 0) === record.total;
  })) throw new Error("잘못된 기록");
  return records;
}

function rankedRecords(records) {
  let rank = 0;
  let previousScore = null;
  return [...records].sort((a, b) => (b.points ?? b.total) - (a.points ?? a.total) || a.completedAt.localeCompare(b.completedAt))
    .map((record, index) => {
      if ((record.points ?? record.total) !== previousScore) rank = index + 1;
      previousScore = record.points ?? record.total;
      return { ...record, rank };
    });
}

function saveResult(name, storage) {
  if (!game.completedAt || game.saved || !validName(name)) return false;
  const records = readRecords(storage); // Preserve unreadable records by refusing to overwrite them.
  records.push({ name: name.trim(), ...scores(), mode: game.mode, questionCount: game.questions.length, completedAt: game.completedAt });
  storage.setItem(recordKey(game.mode), JSON.stringify(records));
  game.saved = true;
  return true;
}

if (typeof module !== "undefined") module.exports = { game, startGame, answer, nextQuestion, scores, RECORD_KEY, validName, readRecords, rankedRecords, saveResult, dailyQuestions, expireQuestion, useHint, recordKey };

if (typeof document !== "undefined") {
  const byId = id => document.getElementById(id);
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  };

  byId("categories").replaceChildren(...categories.map(category => make("li", category)));

  function renderRanking() {
    const list = byId("ranking-list");
    list.replaceChildren();
    try {
      const records = rankedRecords(readRecords(window.localStorage));
      byId("ranking-status").textContent = records.length ? "" : "아직 저장된 기록이 없습니다.";
      records.forEach(record => {
        const row = make("li", "", "ranking-row");
        row.append(make("strong", `${record.rank}위`), make("span", record.name, "ranking-name"),
          make("strong", `${record.points ?? record.total}점 · ${record.total}/${record.questionCount || 50} 정답`), make("time", new Date(record.completedAt).toLocaleString("ko-KR")));
        row.lastChild.dateTime = record.completedAt;
        list.append(row);
      });
    } catch {
      byId("ranking-status").textContent = "기록을 읽을 수 없습니다. 저장 권한이나 기존 기록을 확인해 주세요. 기존 기록은 변경하지 않았으며 퀴즈는 계속할 수 있습니다.";
    }
  }

  function render() {
    const completed = game.index === game.questions.length;
    byId("intro").hidden = game.started;
    byId("quiz").hidden = !game.started || completed;
    byId("result").hidden = !game.started || !completed;
    if (!game.started) return;

    const { total, byCategory } = scores();
    if (completed) {
      byId("total-score").textContent = scores().points;
      byId("score-maximum").textContent = ` / ${game.questions.length * (game.mode === "speed" ? 10 : 1)}점`;
      byId("result-summary").textContent = `${game.questions.length}문제 중 ${total}문제 정답 · ${scores().points}점. 현재 모드의 결과입니다.`;
      byId("category-scores").replaceChildren(...categories.map(category => {
        const row = document.createElement("div");
        row.append(make("dt", category), make("dd", `${byCategory[category]} / ${game.questions.filter(q => q.category === category).length}`));
        return row;
      }));
      renderRanking();
      return;
    }

    const question = game.questions[game.index];
    const selected = game.answers[game.index];
    const answered = selected !== undefined;
    byId("category").textContent = question.category;
    byId("position").textContent = `${game.index + 1} / ${game.questions.length}문제`;
    byId("progress").max = game.questions.length;
    byId("progress").value = game.answers.length;
    byId("topic").textContent = question.topic;
    byId("current-score").textContent = `현재 ${scores().points}점`;
    byId("question").textContent = question.question;
    byId("options").replaceChildren(...question.options.map((option, index) => {
      const button = make("button", "", "option");
      button.type = "button";
      button.disabled = answered;
      if (!answered && game.hints.includes(game.index)) {
        const wrong = question.options.findIndex((_, i) => i !== question.answer_index);
        button.disabled = index !== question.answer_index && index !== wrong;
      }
      button.append(make("span", index + 1, "option-number"), make("span", option));
      if (answered && index === question.answer_index) {
        button.classList.add("correct");
        button.append(make("span", index === selected ? "선택 · 정답" : "정답", "answer-tag"));
      } else if (answered && index === selected) {
        button.classList.add("wrong");
        button.append(make("span", "선택 · 오답", "answer-tag"));
      }
      button.addEventListener("click", () => {
        const accepted = answer(index);
        render(); // A click at the deadline may expire the question instead of accepting an answer.
        if (accepted || game.answers[game.index] === -1) {
          byId("next").focus();
        }
      });
      return button;
    }));

    const feedback = byId("feedback");
    feedback.replaceChildren();
    if (answered) {
      const correct = selected === question.answer_index;
      const title = make("p", correct ? `정답입니다! +${game.mode === "speed" ? (game.hints.includes(game.index) ? 8 : 10) : 1}점` : selected === -1 ? "시간 초과입니다. 해설을 확인해 보세요." : "오답입니다. 해설을 확인해 보세요.", "feedback-title");
      if (!correct) title.classList.add("wrong");
      feedback.append(title, make("p", `정답: ${question.answer_index + 1}번 · ${question.options[question.answer_index]}`), make("p", question.explanation));
      const links = document.createElement("ul");
      question.sources.forEach(source => {
        const item = document.createElement("li");
        const url = new URL(source.url);
        if (url.protocol !== "https:") return;
        const link = make("a", `${source.publisher} · ${source.title}`);
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        item.append(link, make("span", ` (확인: ${source.checked_on})`));
        links.append(item);
      });
      feedback.append(make("p", "출처에서 근거 확인하기"), links);
    }
    byId("hint-button").hidden = game.mode === "normal";
    byId("hint-button").disabled = answered || game.hints.includes(game.index);
    byId("hint-status").textContent = game.hints.includes(game.index) ? "보기 2개로 좁혔습니다. 스피드 모드에서 이 문제의 정답 점수는 8점입니다." : "";
    byId("timer-status").hidden = game.mode !== "speed";
    updateCountdown();
    byId("next").disabled = !answered;
    byId("next").textContent = game.index === game.questions.length - 1 ? "최종 결과 보기 →" : "다음 문제 →";
  }

  function begin() {
    startGame(byId("game-mode").value, byId("practice-category").value);
    byId("save-form").reset();
    byId("player-name").setCustomValidity("");
    byId("save-record").disabled = false;
    byId("save-status").textContent = "";
    render();
    byId("question").focus();
  }
  byId("practice-category").replaceChildren(...categories.map(category => {
    const option = make("option", category); option.value = category; return option;
  }));
  function updateCountdown() {
    if (game.mode !== "speed" || !game.started || game.index >= game.questions.length) return;
    const remaining = game.answers[game.index] === undefined ? Math.max(0, Math.ceil((game.deadline - Date.now()) / 1000)) : 0;
    byId("timer-status").textContent = game.answers[game.index] === -1 ? "시간 초과 · 오답 처리되었습니다." : `제한 시간: ${remaining}초`;
  }
  setInterval(() => { if (expireQuestion()) render(); else updateCountdown(); }, 250);
  byId("hint-button").addEventListener("click", () => { if (useHint()) render(); });
  byId("export-records").addEventListener("click", () => {
    try {
      const records = ["normal", "speed", "practice", "daily"].flatMap(mode => readRecords(window.localStorage, mode).map(record => ({...record, mode: record.mode || "normal"})));
      const blob = new Blob([JSON.stringify({version: 1, records}, null, 2)], {type: "application/json"});
      const url = URL.createObjectURL(blob); const a = document.createElement("a");
      a.href = url; a.download = "quiz-records.json"; a.click(); URL.revokeObjectURL(url);
      byId("export-status").textContent = "기록을 내보냈습니다. 이름과 점수가 포함되므로 공유 전 확인하세요.";
    } catch { byId("export-status").textContent = "기록을 읽지 못했습니다. 기존 데이터는 변경하지 않았습니다."; }
  });
  byId("start").addEventListener("click", begin);
  byId("restart").addEventListener("click", begin);
  byId("choose-mode").addEventListener("click", () => { game.started = false; render(); byId("game-mode").focus(); });
  byId("player-name").addEventListener("input", () => byId("player-name").setCustomValidity(""));
  byId("save-form").addEventListener("submit", event => {
    event.preventDefault();
    const input = byId("player-name");
    if (!validName(input.value)) {
      input.setCustomValidity("앞뒤 공백을 제외한 이름을 1~20자로 입력해 주세요.");
      input.reportValidity();
      return;
    }
    try {
      if (!saveResult(input.value, window.localStorage)) return;
      input.value = input.value.trim();
      byId("save-record").disabled = true;
      byId("save-status").textContent = "이번 결과를 저장했습니다.";
      renderRanking();
    } catch {
      byId("save-status").textContent = "저장하지 못했습니다. 저장 권한·용량이나 기존 기록을 확인해 주세요. 기존 기록은 변경하지 않았습니다. 결과 확인과 다시 도전은 가능합니다.";
    }
  });
  byId("next").addEventListener("click", () => {
    if (nextQuestion()) {
      render();
      byId(game.index === game.questions.length ? "result-title" : "question").focus();
    }
  });
  render();
}
