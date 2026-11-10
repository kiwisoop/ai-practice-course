(function () {
"use strict";
const defaultRules = {
  업무: ["회사", "회의", "고객", "출근", "보고서"],
  과제: ["과제", "제출", "레포트", "리포트", "팀플"],
  공부: ["공부", "시험", "복습", "강의", "독서"],
  취미: ["영화", "게임", "여행", "운동", "그림"],
  개발: ["코딩", "개발", "디버그", "깃허브", "github", "코드"],
  개인: ["병원", "장보기", "청소", "은행", "약속"],
};
function validateRules(rules) {
  if (!rules || Object.keys(rules).length !== 6 || !Object.keys(defaultRules).every(category =>
    Array.isArray(rules[category]) && rules[category].length <= 24 &&
    rules[category].every(word => typeof word === "string" && word.trim() === word && word.length > 0 && word.length <= 20))) {
    throw new Error("각 카테고리에 20자 이하 키워드를 최대 24개 입력하세요.");
  }
  return rules;
}
function classify(title, rules = defaultRules) {
  validateRules(rules);
  const text = title.toLocaleLowerCase("ko-KR");
  let result = null;
  let length = 0;
  for (const [category, words] of Object.entries(rules)) {
    for (const word of words) {
      if (text.includes(word.toLocaleLowerCase("ko-KR")) && word.length > length) {
        result = category;
        length = word.length;
      }
    }
  }
  return result;
}
const classifier = { defaultRules, validateRules, classify };
if (typeof module !== "undefined") module.exports = classifier;
else globalThis.KIWIBIRD_CLASSIFIER = classifier;

})();
