"use strict";
const reportCategories = ["한국사", "과학", "지리", "일반상식", "컴퓨터공학"];
function validateRecords(data) {
  if (!data || data.version !== 1 || !Array.isArray(data.records) || data.records.length > 10000) throw new Error("기록 파일 형식을 확인하세요.");
  for (const r of data.records) {
    if (!r || typeof r !== "object") throw new Error("기록 형식을 확인하세요.");
    const mode = r.mode || "normal", count = r.questionCount ?? 50;
    if (typeof r.name !== "string" || !r.name.trim() || r.name.length > 20 ||
        !["normal", "speed", "practice", "daily"].includes(mode) || count !== (["normal", "speed"].includes(mode) ? 50 : 10) ||
        !Number.isInteger(r.total) || r.total < 0 || r.total > count ||
        typeof r.completedAt !== "string" || !Number.isFinite(Date.parse(r.completedAt)) ||
        !r.byCategory || Object.keys(r.byCategory).length !== 5 || !reportCategories.every(c => Number.isInteger(r.byCategory[c]) && r.byCategory[c] >= 0 && r.byCategory[c] <= 10) ||
        Object.values(r.byCategory).reduce((s, v) => s + v, 0) !== r.total ||
        (mode === "speed" && r.points === undefined) ||
        (r.points !== undefined && (!Number.isInteger(r.points) || (mode === "speed" ? r.points < r.total * 8 || r.points > r.total * 10 || r.points % 2 !== 0 : r.points !== r.total)))) throw new Error("잘못된 점수·이름·완료 기록이 있습니다. 기존 보고서는 유지됩니다.");
  }
  return data.records.map(r => ({...r, name: r.name.trim(), mode: r.mode || "normal", questionCount: r.questionCount ?? 50, points: r.points ?? r.total}));
}
function summarizeRecords(records, mode) {
  const selected = records.filter(r => r.mode === mode).sort((a, b) => b.points - a.points || a.completedAt.localeCompare(b.completedAt));
  let previous = null, rank = 0;
  const rows = selected.map((r, i) => {
    if (r.points !== previous) rank = i + 1;
    previous = r.points;
    const percent = 100 * r.total / r.questionCount;
    return {...r, rank, percent, grade: percent >= 90 ? "A" : percent >= 80 ? "B" : percent >= 70 ? "C" : percent >= 60 ? "D" : "F"};
  });
  return {rows, average: rows.length ? rows.reduce((s, r) => s + r.percent, 0) / rows.length : 0,
    categories: Object.fromEntries(reportCategories.map(c => [c, rows.length ? rows.reduce((s, r) => s + r.byCategory[c], 0) / rows.length : 0]))};
}
function csvCell(value) {
  let text = String(value);
  if (/^[\s]*[=+\-@]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
}
if (typeof module !== "undefined") module.exports = {validateRecords, summarizeRecords, csvCell};
if (typeof document !== "undefined") {
  let records = [];
  const byId = id => document.getElementById(id);
  const summary = () => summarizeRecords(records, byId("report-mode").value);
  function render() {
    const data = summary();
    byId("report-summary").textContent = `완료 기록 ${data.rows.length}개 · 평균 정답률 ${data.average.toFixed(1)}%`;
    byId("report-rows").replaceChildren(...data.rows.map(r => {
      const tr = document.createElement("tr");
      for (const value of [r.rank, r.name, r.points, r.percent.toFixed(1) + "%", r.grade, new Date(r.completedAt).toLocaleString("ko-KR")]) {
        const td = document.createElement("td"); td.textContent = value; tr.append(td);
      }
      return tr;
    }));
    byId("report-categories").replaceChildren(...reportCategories.map(c => { const li = document.createElement("li"); li.textContent = `${c}: ${data.categories[c].toFixed(1)}문제`; return li; }));
  }
  byId("records-file").addEventListener("change", async event => {
    try {
      const files = [...event.target.files];
      if (files.reduce((s, f) => s + f.size, 0) > 10 * 1024 * 1024) throw new Error("파일 전체 크기는 10MB 이하여야 합니다.");
      const imported = [];
      for (const file of files) imported.push(...validateRecords(JSON.parse(await file.text())));
      const combined = [...records, ...imported];
      if (combined.length > 10000) throw new Error("기록은 최대 10,000개까지 분석합니다.");
      const unique = new Map(combined.map(r => [JSON.stringify(r), r]));
      records = [...unique.values()]; render();
      byId("report-status").textContent = "기록을 불러왔습니다. 같은 기록의 재가져오기는 중복 집계하지 않습니다.";
    } catch (error) { byId("report-status").textContent = `불러오지 못했습니다: ${error.message}`; }
  });
  byId("report-mode").addEventListener("change", render);
  function download(content, type, name) {
    const url = URL.createObjectURL(new Blob([content], {type})); const a = document.createElement("a");
    a.href = url; a.download = name; a.click(); URL.revokeObjectURL(url);
  }
  byId("export-csv").addEventListener("click", () => {
    const lines = [["순위", "이름", "모드", "점수", "정답률", "등급", "완료 시각"], ...summary().rows.map(r => [r.rank, r.name, r.mode, r.points, r.percent.toFixed(1), r.grade, r.completedAt])];
    download("\ufeff" + lines.map(row => row.map(csvCell).join(",")).join("\r\n"), "text/csv;charset=utf-8", "teacher_report.csv");
  });
  byId("export-html").addEventListener("click", () => {
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll("link[rel=stylesheet]").forEach(node => node.remove());
    const style = document.createElement("style");
    style.textContent = "body{font-family:system-ui,sans-serif;margin:2rem;color:#1d2635}main{max-width:1000px;margin:auto}table{border-collapse:collapse;width:100%;text-align:left}th,td{padding:.7rem;border-bottom:1px solid #ccc;overflow-wrap:anywhere}";
    clone.querySelector("head").append(style);
    clone.querySelectorAll("script, #report-controls, #report-status").forEach(node => node.remove());
    download("<!doctype html>" + clone.outerHTML, "text/html;charset=utf-8", "teacher_report.html");
  });
  render();
}
