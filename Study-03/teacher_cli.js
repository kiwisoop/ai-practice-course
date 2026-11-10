"use strict";
// Local records only. Share the browser report's validation and scoring.
const fs = require("node:fs");
const {parseArgs} = require("node:util");
const {validateRecords, summarizeRecords, csvCell} = require("./teacher.js");
function createReport(records, mode, format) {
  if (!["normal", "speed", "practice", "daily"].includes(mode)) throw new Error("Unknown mode");
  const {rows, average} = summarizeRecords(records, mode);
  if (format === "json") return JSON.stringify({mode, average, rows}, null, 2);
  const table = [["Rank", "Name", "Points", "Correct %", "Grade", "Completed"], ...rows.map(r => [r.rank, r.name, r.points, r.percent.toFixed(1), r.grade, r.completedAt])];
  if (format === "csv") return "\ufeff" + table.map(row => row.map(csvCell).join(",")).join("\r\n");
  if (format !== "html") throw new Error("Use json, csv or html");
  const escape = value => String(value).replace(/[&<>"']/g, ch => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[ch]));
  return '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiz report</title><style>body{font-family:system-ui;margin:2rem}table{border-collapse:collapse}th,td{padding:.7rem;border:1px solid #ccc}</style><h1>Quiz report</h1><p>' + escape(mode) + ' / Average: ' + average.toFixed(1) + '%</p><table>' + table.map((row, i) => '<tr>' + row.map(value => `<${i ? "td" : "th"}>${escape(value)}</${i ? "td" : "th"}>`).join("") + '</tr>').join("") + '</table><p>Learning example: A ≥90%, B ≥80%, C ≥70%, D ≥60%, F otherwise. Not official grades.</p></html>';
}
if (require.main === module) {
  try {
    const {values} = parseArgs({options:{records:{type:"string", multiple:true},mode:{type:"string",default:"normal"},format:{type:"string",default:"json"},output:{type:"string"}}});
    if (!values.records?.length) throw new Error("Usage: node teacher_cli.js --records FILE [--mode normal] [--format json|csv|html] [--output FILE]");
    const imported = values.records.flatMap(file => {
      if (fs.statSync(file).size > 10 * 1024 * 1024) throw new Error("File exceeds 10MB");
      return validateRecords(JSON.parse(fs.readFileSync(file,"utf8")));
    });
    if (imported.length > 10000) throw new Error("Maximum 10,000 records");
    const unique = [...new Map(imported.map(r => [JSON.stringify(r),r])).values()];
    const content = createReport(unique, values.mode, values.format);
    if (values.output) fs.writeFileSync(values.output, content, {flag:"wx"}); // Never overwrite an existing report.
    else process.stdout.write(content + "\n");
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}
module.exports = {createReport};
