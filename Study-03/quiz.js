"use strict";

const { questions, categories } = globalThis.QUIZ_DATA;
const game = { started: false, index: 0, answers: [], completedAt: null, saved: false };
const RECORD_KEY = "study03.records.v1";

function startGame() {
  game.started = true;
  game.index = 0;
  game.answers = [];
  game.completedAt = null;
  game.saved = false;
}

function answer(choice) {
  if (!game.started || game.index >= questions.length || game.answers[game.index] !== undefined ||
      !Number.isInteger(choice) || choice < 0 || choice >= 4) return false;
  game.answers[game.index] = choice;
  return true;
}

function nextQuestion() {
  if (!game.started || game.index >= questions.length || game.answers[game.index] === undefined) return false;
  game.index += 1;
  if (game.index === questions.length) game.completedAt = new Date().toISOString();
  return true;
}

function scores() {
  const byCategory = Object.fromEntries(categories.map(category => [category, 0]));
  game.answers.forEach((choice, index) => {
    if (choice === questions[index].answer_index) byCategory[questions[index].category] += 1;
  });
  return { byCategory, total: Object.values(byCategory).reduce((sum, score) => sum + score, 0) };
}

function validName(name) {
  return typeof name === "string" && name.trim().length >= 1 && name.trim().length <= 20;
}

function readRecords(storage) {
  const raw = storage.getItem(RECORD_KEY);
  const records = raw === null ? [] : JSON.parse(raw);
  if (!Array.isArray(records) || !records.every(record => {
    if (!record || !validName(record.name) || record.name !== record.name.trim() ||
        !Number.isInteger(record.total) || record.total < 0 || record.total > 50 ||
        typeof record.completedAt !== "string" || !Number.isFinite(Date.parse(record.completedAt)) ||
        new Date(record.completedAt).toISOString() !== record.completedAt ||
        !record.byCategory || typeof record.byCategory !== "object") return false;
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
  return [...records].sort((a, b) => b.total - a.total || a.completedAt.localeCompare(b.completedAt))
    .map((record, index) => {
      if (record.total !== previousScore) rank = index + 1;
      previousScore = record.total;
      return { ...record, rank };
    });
}

function saveResult(name, storage) {
  if (!game.completedAt || game.saved || !validName(name)) return false;
  const records = readRecords(storage); // Preserve unreadable records by refusing to overwrite them.
  records.push({ name: name.trim(), ...scores(), completedAt: game.completedAt });
  storage.setItem(RECORD_KEY, JSON.stringify(records));
  game.saved = true;
  return true;
}

if (typeof module !== "undefined") module.exports = { game, startGame, answer, nextQuestion, scores, RECORD_KEY, validName, readRecords, rankedRecords, saveResult };

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
          make("strong", `${record.total}점`), make("time", new Date(record.completedAt).toLocaleString("ko-KR")));
        row.lastChild.dateTime = record.completedAt;
        list.append(row);
      });
    } catch {
      byId("ranking-status").textContent = "기록을 읽을 수 없습니다. 저장 권한이나 기존 기록을 확인해 주세요. 기존 기록은 변경하지 않았으며 퀴즈는 계속할 수 있습니다.";
    }
  }

  function render() {
    const completed = game.index === questions.length;
    byId("intro").hidden = game.started;
    byId("quiz").hidden = !game.started || completed;
    byId("result").hidden = !game.started || !completed;
    if (!game.started) return;

    const { total, byCategory } = scores();
    if (completed) {
      byId("total-score").textContent = total;
      byId("result-summary").textContent = `50문제 중 ${total}문제를 맞혔습니다. 분야별 결과를 확인해 보세요.`;
      byId("category-scores").replaceChildren(...categories.map(category => {
        const row = document.createElement("div");
        row.append(make("dt", category), make("dd", `${byCategory[category]} / 10`));
        return row;
      }));
      renderRanking();
      return;
    }

    const question = questions[game.index];
    const selected = game.answers[game.index];
    const answered = selected !== undefined;
    byId("category").textContent = question.category;
    byId("position").textContent = `${game.index + 1} / ${questions.length}문제`;
    byId("progress").value = game.answers.length;
    byId("topic").textContent = question.topic;
    byId("current-score").textContent = `현재 ${total}점`;
    byId("question").textContent = question.question;
    byId("options").replaceChildren(...question.options.map((option, index) => {
      const button = make("button", "", "option");
      button.type = "button";
      button.disabled = answered;
      button.append(make("span", index + 1, "option-number"), make("span", option));
      if (answered && index === question.answer_index) {
        button.classList.add("correct");
        button.append(make("span", index === selected ? "선택 · 정답" : "정답", "answer-tag"));
      } else if (answered && index === selected) {
        button.classList.add("wrong");
        button.append(make("span", "선택 · 오답", "answer-tag"));
      }
      button.addEventListener("click", () => {
        if (answer(index)) {
          render();
          byId("next").focus();
        }
      });
      return button;
    }));

    const feedback = byId("feedback");
    feedback.replaceChildren();
    if (answered) {
      const correct = selected === question.answer_index;
      const title = make("p", correct ? "정답입니다! +1점" : "오답입니다. 해설을 확인해 보세요.", "feedback-title");
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
    byId("next").disabled = !answered;
    byId("next").textContent = game.index === questions.length - 1 ? "최종 결과 보기 →" : "다음 문제 →";
  }

  function begin() {
    startGame();
    byId("save-form").reset();
    byId("player-name").setCustomValidity("");
    byId("save-record").disabled = false;
    byId("save-status").textContent = "";
    render();
    byId("question").focus();
  }
  byId("start").addEventListener("click", begin);
  byId("restart").addEventListener("click", begin);
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
      byId(game.index === questions.length ? "result-title" : "question").focus();
    }
  });
  render();
}
