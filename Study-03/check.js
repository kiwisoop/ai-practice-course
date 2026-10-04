"use strict";

// Run with: node check.js. No packages needed.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
require("./questions-data.js");
const data = JSON.parse(fs.readFileSync(path.join(__dirname, "questions.json"), "utf8"));
assert.deepEqual(globalThis.QUIZ_DATA, data, "Regenerate questions-data.js after changing questions.json");
const { game, startGame, answer, nextQuestion, scores, RECORD_KEY, validName, readRecords, rankedRecords, saveResult } = require("./quiz.js");
assert.equal(data.questions.length, 50);
assert.deepEqual(data.categories, ["한국사", "과학", "지리", "일반상식", "컴퓨터공학"]);
assert.equal(new Set(data.questions.map(q => q.id)).size, 50);
assert.equal(new Set(data.questions.map(q => q.question)).size, 50);
data.categories.forEach((category, index) => {
  assert.equal(data.questions.filter(q => q.category === category).length, 10);
  assert.ok(data.questions.slice(index * 10, index * 10 + 10).every(q => q.category === category));
});
data.questions.forEach(q => {
  assert.equal(q.options.length, 4);
  assert.equal(new Set(q.options).size, 4);
  assert.ok(Number.isInteger(q.answer_index) && q.answer_index >= 0 && q.answer_index < 4);
  assert.ok(q.question && q.explanation && q.sources.length);
  q.sources.forEach(s => {
    assert.equal(new URL(s.url).protocol, "https:");
    assert.ok(s.publisher && s.title && s.checked_on && s.evidence_summary);
  });
});
assert.equal(answer(0), false, "Cannot answer before starting");
assert.equal(nextQuestion(), false);
for (const mode of ["correct", "wrong", "mixed"]) {
  startGame();
  assert.equal(scores().total, 0);
  let expected = 0;
  data.questions.forEach((q, index) => {
    assert.equal(game.index, index);
    assert.equal(nextQuestion(), false, "Cannot skip unanswered questions");
    for (const bad of [-1, 4, 1.5, NaN, "1", null]) assert.equal(answer(bad), false);
    const correct = mode === "correct" || (mode === "mixed" && index % 2 === 0);
    assert.equal(answer(correct ? q.answer_index : (q.answer_index + 1) % 4), true);
    expected += Number(correct);
    assert.equal(answer(q.answer_index), false, "Cannot score twice");
    assert.equal(scores().total, expected);
    assert.equal(Object.values(scores().byCategory).reduce((sum, value) => sum + value, 0), expected);
    assert.equal(nextQuestion(), true);
  });
  assert.equal(game.index, 50);
  assert.equal(scores().total, mode === "correct" ? 50 : mode === "wrong" ? 0 : 25);
  assert.ok(Object.values(scores().byCategory).every(value => value === (mode === "correct" ? 10 : mode === "wrong" ? 0 : 5)));
  assert.equal(answer(0), false);
  assert.equal(nextQuestion(), false);
}
startGame();
assert.equal(game.index, 0);
assert.deepEqual(game.answers, []);
assert.equal(scores().total, 0);
let stored = null;
const storage = { getItem: () => stored, setItem: (key, value) => { assert.equal(key, RECORD_KEY); stored = value; } };
const complete = correct => {
  startGame();
  data.questions.forEach(q => { answer(correct ? q.answer_index : (q.answer_index + 1) % 4); nextQuestion(); });
};
assert.equal(saveResult("이름", storage), false, "Cannot save unfinished games");
assert.equal(validName("   "), false);
assert.equal(validName("가".repeat(21)), false);
assert.equal(validName("가".repeat(20)), true);
complete(true);
assert.equal(saveResult(" ", storage), false);
assert.equal(saveResult("가".repeat(21), storage), false);
game.completedAt = "2026-10-05T01:00:00.000Z";
assert.equal(saveResult("  <b>이름</b>  ", storage), true);
assert.equal(saveResult("중복", storage), false);
assert.equal(readRecords(storage)[0].name, "<b>이름</b>");
const first = readRecords(storage)[0];
complete(true);
game.completedAt = "2026-10-05T00:00:00.000Z";
assert.equal(saveResult("동점", storage), true);
complete(false);
assert.equal(saveResult("0점", storage), true);
assert.deepEqual(rankedRecords(readRecords(storage)).map(r => r.rank), [1, 1, 3]);
assert.equal(rankedRecords(readRecords(storage))[0].name, "동점");
startGame();
assert.equal(readRecords(storage).length, 3, "Restart preserves records");
complete(true);
for (const bad of ["{", "null", "{}", JSON.stringify([{ ...first, total: 49 }]),
  JSON.stringify([{ ...first, completedAt: "bad" }]), JSON.stringify([{ ...first, byCategory: { ...first.byCategory, 한국사: 11 } }])]) {
  stored = bad;
  assert.throws(() => readRecords(storage));
  assert.throws(() => saveResult("이름", storage));
  assert.equal(stored, bad, "Invalid records must not be overwritten");
  assert.equal(game.saved, false);
}
stored = "[]";
assert.throws(() => saveResult("이름", { ...storage, setItem: () => { throw new Error("quota"); } }));
assert.throws(() => saveResult("이름", { getItem: () => { throw new Error("blocked"); } }));
assert.equal(game.saved, false);
assert.equal(stored, "[]");
assert.equal(saveResult("재시도", storage), true);
console.log("PASS: ranking, ties, trimmed names, completion-only/one-time save, preserved records, invalid data and storage failures.");
console.log("PASS: source data, 50 questions, category order, scoring 50/0/25, duplicate/invalid answers, no skips, completion and restart.");
