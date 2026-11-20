# 인공지능활용실습 — 한 학기 프로젝트 모음

> 국립목포대학교 **인공지능활용실습** 수업에서 AI 코딩 도구(Claude Code·Codex)와 함께 만든 결과물입니다.
> 손글씨 인식으로 시작해 API·에이전트·MCP를 차례로 익혔고, 기말 프로젝트 **3년 다이어리**로 마무리했습니다.

**[▶ 기말 프로젝트 온라인 시연](https://kiwisoop.github.io/ai-practice-course/Term-Project/)** · 프로젝트 7개 · 교재 16장 실습

![3년 다이어리 메인 화면](Term-Project/docs/images/01-main.jpg)

---

## 한 학기 흐름

```mermaid
flowchart LR
    A["프롬프트<br/>교재 01–02"] --> B["Claude Code 시작<br/>Study-01"]
    B --> C["단계별 개발<br/>Study-02"]
    C --> D["커스텀 명령어<br/>Study-03"]
    D --> E["API 연결<br/>Study-04"]
    E --> F["서브에이전트<br/>Study-04·05"]
    F --> G["MCP 자동화<br/>Study-06"]
    G --> H["기말 프로젝트<br/>3년 다이어리"]
```

---

## 프로젝트

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="Study-01/README.md"><img src="docs/images/study01.jpg" alt="손글씨 숫자 입력 화면"></a>
      <h3>01 · 손글씨 숫자 인식</h3>
      <sub>교재 03</sub>
      <p>숫자를 그리면 MNIST로 학습한 모델이 숫자와 신뢰도를 알려 줍니다. 데스크톱(Tkinter)과 웹 두 가지 버전이 있습니다.</p>
      <sub>🐍 Python · TensorFlow</sub>
    </td>
    <td width="50%" valign="top">
      <a href="Study-02/README.md"><img src="docs/images/study02.jpg" alt="Kiwibird 할 일 관리 화면"></a>
      <h3>02 · Kiwibird 할 일 관리</h3>
      <sub>교재 04–06</sub>
      <p>할 일을 모두 끝내면 둥지의 알이 키위새로 바뀝니다. 마감일·우선순위·집중 타이머·자동 분류를 지원합니다.</p>
      <sub>🌐 브라우저만 있으면 실행</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="Study-03/README.md"><img src="docs/images/study03.jpg" alt="출처를 보여 주는 퀴즈 화면"></a>
      <h3>03 · 상식 한 바퀴 퀴즈</h3>
      <sub>교재 07–09</sub>
      <p>모든 문제에 출처가 붙은 50문제 퀴즈입니다. 커스텀 명령어 8개와 교사용 대시보드·보고서를 만들었습니다.</p>
      <sub>🌐 브라우저만 있으면 실행</sub>
    </td>
    <td width="50%" valign="top">
      <a href="Study-04/README.md"><img src="Study-04/screenshots/dashboard.jpg" alt="FridgeChef 대시보드"></a>
      <h3>04 · FridgeChef 냉장고 요리사</h3>
      <sub>교재 11–13</sub>
      <p>냉장고 사진에서 재료를 인식하고 레시피를 추천합니다. 리뷰·최적화·UX 서브에이전트로 코드를 개선했습니다.</p>
      <sub>🐍 Python · Streamlit · 🔑 API 키</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="Study-05/README.md"><img src="Study-05/screenshots/diary-desktop.png" alt="공감 다이어리 화면"></a>
      <h3>05 · 공감 다이어리 · PDF 요약</h3>
      <sub>교재 14</sub>
      <p>역할별 AI 개발팀(서브에이전트 5개)과 함께 일기 공감 앱과 PDF 요약 앱을 만들었습니다.</p>
      <sub>🐍 Python · pypdf · 🔑 API 키</sub>
    </td>
    <td width="50%" valign="top">
      <a href="Study-06/README.md"><img src="Study-06/screenshots/shopping-list-test.png" alt="Playwright로 검사한 쇼핑 리스트"></a>
      <h3>06 · 쇼핑 리스트 + MCP</h3>
      <sub>교재 15–16</sub>
      <p>Notion·Sequential Thinking·Context7·Playwright·GitHub MCP를 실습하고, 쇼핑 리스트 앱을 브라우저에서 자동으로 검사했습니다.</p>
      <sub>🌐 브라우저만 있으면 실행</sub>
    </td>
  </tr>
</table>

### ⭐ 기말 프로젝트 · 3년 다이어리

<table>
  <tr>
    <td width="34%"><img src="Term-Project/docs/images/day-shorts.gif" alt="하루 일기로 만든 쇼츠"></td>
    <td valign="top">
      <h3><a href="Term-Project/README.md">같은 날, 세 해의 이야기</a></h3>
      <p>같은 날짜의 일기를 3년 동안 쌓으면, AI가 일기를 <b>짧은 이야기 · 수채화 · 세로 쇼츠 영상</b>으로 만들어 줍니다.</p>
      <ul>
        <li>학교 API로 Claude가 이야기를 쓰고 GPT Image가 수채화를 그립니다</li>
        <li>FFmpeg로 자막·배경음악을 넣어 720×1280 세로 영상을 합성합니다</li>
        <li>호출 전에 동의와 예상 비용을 확인하고, 같은 일기는 이전 결과를 다시 씁니다</li>
      </ul>
      <p><a href="https://kiwisoop.github.io/ai-practice-course/Term-Project/"><b>▶ 온라인 시연판</b></a>: API를 호출하지 않고 미리 만든 결과로 체험합니다</p>
    </td>
  </tr>
</table>

---

## 교재별 실습 확인표

| 교재 | 실습 내용 | 결과물 |
| :---: | --- | --- |
| 01 | AI 어시스턴트와 바이브 코딩 | 웹 채팅 실습 (파일 없음) |
| 02 | 좋은 프롬프트·PRD 쓰기 | 각 Study의 `PRD.md`에 적용 |
| 03 | Claude Code 설치, 손글씨 인식 | [Study-01](Study-01/README.md) |
| 04 | `/init`·`/model` 등 단계별 프롬프트 | [Study-02](Study-02/README.md) |
| 05 | `/compact`·`/resume`, 자동 분류 | [Study-02](Study-02/README.md) |
| 06 | 화면 캡처로 UI 개선 | [Study-02](Study-02/README.md) |
| 07 | 출처 확인으로 할루시네이션 막기 | [Study-03 출처 검토](Study-03/SOURCE_REVIEW.md) |
| 08 | 커스텀 명령어 만들기 | [Study-03 명령어](Study-03/.claude/commands) |
| 09 | 명령어 체이닝·선생님 모드 | [Study-03 확장 기능](Study-03/EXTENSIONS.md) |
| 10 | Obsidian·Claudian | 개인 볼트에서 진행 (저장소 밖) |
| 11 | API 키 설정·`.gitignore` | [Study-04](Study-04/README.md) |
| 12 | 3단계 PRD로 API 앱 만들기 | [Study-04](Study-04/README.md) |
| 13 | 리뷰·최적화·UX 서브에이전트 | [Study-04 13주차 기록](Study-04/WEEK13.md) |
| 14 | AI 개발팀으로 앱 2개 만들기 | [Study-05](Study-05/README.md) |
| 15 | Notion·Sequential Thinking MCP | [Study-06 노트](Study-06/notion-notes) |
| 16 | Context7·Playwright·GitHub MCP | [Study-06](Study-06/README.md) |

<details>
<summary>교재와 다르게 진행한 부분</summary>

- **도구:** 교재는 Claude Code 기준이지만 일부 실습은 Codex와 함께 했습니다. 그래서 일부 폴더에는 `CLAUDE.md` 대신 `AGENTS.md`가 있습니다.
- **API:** 교재의 OpenRouter 대신 학교에서 제공한 API 게이트웨이를 사용했습니다.
- **교재 06:** 이전 화면을 `web_version` 폴더에 따로 보관하지 않고, 같은 폴더에서 화면을 개선했습니다.
- **교재 09:** `/create-report`·`/export-report` 대신 `/teacher-dashboard`와 교사 화면의 CSV·HTML 내보내기로 구현했습니다.
- **교재 16:** `shopping-list-app` 저장소를 새로 만들지 않고 이 저장소의 Study-06에 올렸습니다.

</details>

---

## 실행 방법

| 필요한 것 | 프로젝트 |
| --- | --- |
| 브라우저만 | Study-02 · Study-03 · Study-06 · 기말 시연판 |
| Python | Study-01 |
| Python + 본인 API 키 | Study-04 · Study-05 · 기말 프로젝트 전체 기능 |

설치 순서는 각 프로젝트 README의 **실행 방법**에 있습니다. API 키는 `.env`에만 저장하며 저장소에는 올리지 않습니다.

## 폴더 구성

```text
ai-practice-course/
├── Study-01/      손글씨 숫자 인식
├── Study-02/      Kiwibird 할 일 관리
├── Study-03/      출처 확인 퀴즈 + 커스텀 명령어
├── Study-04/      FridgeChef + 서브에이전트
├── Study-05/      공감 다이어리 · PDF 요약
├── Study-06/      쇼핑 리스트 + MCP
├── Term-Project/  기말 프로젝트 · 3년 다이어리
└── docs/images/   README용 화면 캡처
```
