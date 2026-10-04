# Study-03 — 50문제와 출처 검토 기록

출처 확인일: 2026-10-01 (한국 시간). 각 분야 10문제, 총 50문제. 기본 난이도는 상식·컴퓨터공학 입문 수준이다.

이 문서는 questions.json에서 생성했다. 게임에서는 questions.json의 answer_index(0부터 시작)를 사용한다. 이 문서는 정답이 포함된 검토용 자료이다.

## 검증 범위

- 각 정답·해설의 핵심 사실을 출처의 본문 또는 공식 서지·작품 정보와 대조했다.
- 보기 4개의 중복과 다른 정답 가능성, 질문의 시점·범위·전제를 검토했다.
- 확정적 사실을 중심으로 선택했다. 모든 문제에 독립된 출처 2개를 적용한 것은 아니다.
- FIDE 자료는 직접 열기가 실패해 공식 도메인 검색 응답의 제2.1조 본문으로 확인했다. 나머지 최종 출처는 페이지 텍스트를 확인했다.
- 이 검토는 AI가 수행한 출처 대조이다. 사람이나 별도 검토자의 재검토는 아직 수행하지 않았다. 이후 기본 게임 구현과 플레이 검증 결과는 README.md에 별도로 기록했다.
- 출처의 본문은 옮겨 싣지 않고 해당 사실을 바탕으로 질문과 해설을 새로 작성했다. 확인일 이후 링크나 내용은 달라질 수 있다.

## 작성 중 확인·수정한 사항

| 대상 | 확인한 문제 | 최종 처리 |
|---|---|---|
| 과학 SCI-07 | 물의 끓는점은 압력과 용질에 따라 달라짐 | 질문에 1기압·순수한 물·약 100°C 조건 반영 |
| 지리 GEO-08 | 가장 크다는 말에 비교 기준이 필요함 | 해양 분지의 표면적을 비교 기준으로 명시 |
| 지리 GEO-10 | 역사적 그리니치 자오선과 현대 GPS 기준선이 일치하지 않음 | 1884년의 역사적 선택을 묻는 문제로 한정 |
| 일반상식 GEN-01 | 조회한 Gutenberg 1514는 로미오와 줄리엣이 아니라 한여름 밤의 꿈이었음 | 올바른 1513 페이지의 제목·저자를 다시 확인 |
| 일반상식 구성 | UNESCO 무형유산 후보 4개 페이지에서 자동 접근 확인 화면만 반환됨 | 미확인 후보를 제외하고 본문을 확인할 수 있는 문제로 구성 |
| 일반상식 GEN-06 | 비슷한 제목의 반 고흐 밤 풍경 작품과 혼동 가능 | 1889년·원제·MoMA 출처로 작품 특정 |
| 일반상식 GEN-10 | 과거 ISBN은 10자리임 | 2007년 이후 신규 부여라는 조건 추가 |
| 컴퓨터공학 CS-01·02 | 주석 기호·연산 결과는 언어에 따라 달라질 수 있음 | Python 3으로 범위 한정 |
| 컴퓨터공학 CS-03 | 이진 탐색의 정렬 전제 누락 가능 | 비교 기준에 따른 정렬 조건 명시 |
| 컴퓨터공학 CS-09 | RFC는 404가 비공개를 뜻할 수도 있으며 영구 삭제를 단정하지 않음 | 표준 명칭을 묻고 해설에 의미의 한계 반영 |
| 컴퓨터공학 CS-10 | DNS를 단순히 IP 주소만 다루는 시스템으로 설명할 위험 | 리졸버의 대표 기능 중 하나라고 한정 |

위 항목은 작성·자료 확인 중의 개선 기록이다. 기존에 실행한 게임의 오류를 재현하거나 /clear 이후 검증한 기록은 아니다.

## 한국사

### HIS-01 · 문자와 인물

훈민정음을 창제한 조선의 왕은 누구인가?

1. 태조
2. 세종
3. 정조
4. 고종

**정답: 2번 — 세종**

해설: 세종이 훈민정음을 창제했다. 창제 완료는 1443년이며 반포와 해례본 간행은 1446년으로 구분한다.

출처: UNESCO — [Hunminjeongum Manuscript](https://www.unesco.org/en/memory-world/hunminjeongum-manuscript?hub=1081)

확인 근거: 자료 본문은 세종이 1443년에 문자 개발을 완료했으며 1446년에 반포를 담은 문헌이 간행되었다고 설명한다.

### HIS-02 · 국가 건국

918년에 고려를 세운 인물은 누구인가?

1. 이성계
2. 궁예
3. 왕건
4. 견훤

**정답: 3번 — 왕건**

해설: 고려를 세운 인물은 태조 왕건이다.

출처: 문화체육관광부 Korea.net — [Seoul exhibition honors 1,100 years of Goryeo Dynasty artworks](https://www.korea.net/NewsFocus/Culture/view?articleId=166086)

확인 근거: Korea.net 본문은 고려의 연대를 918~1392년으로 제시하고 창건자를 태조 왕건으로 명시한다.

### HIS-03 · 시대와 연도

조선이 건국된 해는 언제인가?

1. 918년
2. 1392년
3. 1446년
4. 1897년

**정답: 2번 — 1392년**

해설: 조선은 1392년에 건국되었다.

출처: 국립민속박물관 — [History of Korea — Korean Culture Box](https://www.nfm.go.kr/k-box/ui/annyeong/history.do?lang=en)

확인 근거: 박물관의 Joseon 연표에 1392년 고려 멸망과 조선 건국이 명시되어 있다.

### HIS-04 · 불교 문화유산

8세기에 석굴암과 불국사를 조성한 시대의 나라는 무엇인가?

1. 고려
2. 백제
3. 조선
4. 신라

**정답: 4번 — 신라**

해설: 석굴암과 불국사는 8세기 신라의 불교 건축 유산이다.

출처: UNESCO 세계유산센터 — [Seokguram Grotto and Bulguksa Temple](https://whc.unesco.org/en/list/736/)

확인 근거: Outstanding Universal Value의 Brief synthesis는 8세기 신라 왕조 아래 조성되었다고 설명한다.

### HIS-05 · 기록 문화유산

팔만대장경 목판을 보관하는 장경판전이 있는 사찰은 어디인가?

1. 해인사
2. 불국사
3. 통도사
4. 송광사

**정답: 1번 — 해인사**

해설: 해인사의 장경판전은 고려대장경 목판을 보관하는 건물이다.

출처: UNESCO 세계유산센터 — [Haeinsa Temple Janggyeong Panjeon](https://whc.unesco.org/en/list/737/)

확인 근거: 유산 설명과 Brief synthesis는 해인사의 장경판전이 Tripitaka Koreana 목판을 보관한다고 명시한다.

### HIS-06 · 왕실 제도

조선의 역대 왕과 왕비의 신위를 모신 왕실 사당은 무엇인가?

1. 성균관
2. 종묘
3. 첨성대
4. 독립문

**정답: 2번 — 종묘**

해설: 종묘는 조선의 왕과 왕비의 신위를 모시고 제례를 지내는 왕실 사당이다.

출처: UNESCO 세계유산센터 — [Jongmyo Shrine](https://whc.unesco.org/en/list/738/)

확인 근거: Brief synthesis는 종묘가 조선의 옛 왕과 왕비의 신위를 모시는 사당이라고 설명한다.

### HIS-07 · 인물과 건축

조선 후기 수원 화성의 건설을 추진한 왕은 누구인가?

1. 세조
2. 영조
3. 정조
4. 순종

**정답: 3번 — 정조**

해설: 수원 화성은 18세기 말 정조가 건설한 성곽이다.

출처: UNESCO 세계유산센터 — [Hwaseong Fortress](https://whc.unesco.org/en/list/817/)

확인 근거: Brief synthesis는 화성이 조선의 정조에 의해 18세기 말 건설되었다고 명시한다.

### HIS-08 · 백제의 수도

백제의 옛 수도 웅진은 오늘날 어느 도시에 해당하는가?

1. 공주
2. 경주
3. 서울
4. 개성

**정답: 1번 — 공주**

해설: 웅진은 오늘날의 공주에 해당한다.

출처: UNESCO 세계유산센터 — [Baekje Historic Areas](https://whc.unesco.org/en/list/1477/)

확인 근거: 유산 설명은 웅진을 현재의 공주로, 사비를 현재의 부여로 구분한다.

### HIS-09 · 왕궁의 시대

창덕궁을 처음 조성한 왕조는 무엇인가?

1. 백제
2. 신라
3. 고려
4. 조선

**정답: 4번 — 조선**

해설: 창덕궁은 조선 시대인 15세기에 조성된 궁궐이다.

출처: UNESCO 세계유산센터 — [Changdeokgung Palace Complex](https://whc.unesco.org/en/list/816/)

확인 근거: Brief synthesis는 창덕궁이 조선 왕조의 15세기에 건설되었다고 설명한다.

### HIS-10 · 근대사

대한제국이 선포된 해는 언제인가?

1. 1876년
2. 1897년
3. 1910년
4. 1948년

**정답: 2번 — 1897년**

해설: 대한제국은 1897년에 선포되었다.

출처: 국립민속박물관 — [History of Korea — Korean Culture Box](https://www.nfm.go.kr/k-box/ui/annyeong/history.do?lang=en)

확인 근거: Joseon 연표에 대한제국 선포 연도가 1897년으로 명시되어 있다.

## 과학

### SCI-01 · 물리·전류

전류의 SI 기본 단위는 무엇인가?

1. 볼트(V)
2. 와트(W)
3. 암페어(A)
4. 옴(Ω)

**정답: 3번 — 암페어(A)**

해설: 전류의 SI 기본 단위는 암페어이며 기호는 A이다.

출처: 미국 국립표준기술연구소 NIST — [Ampere: Introduction](https://www.nist.gov/si-redefinition/ampere-introduction)

확인 근거: 본문은 ampere (A)를 전류의 SI 기본 단위로 명시한다.

### SCI-02 · 물리·온도

열역학적 온도의 SI 기본 단위는 무엇인가?

1. 켈빈(K)
2. 줄(J)
3. 뉴턴(N)
4. 파스칼(Pa)

**정답: 1번 — 켈빈(K)**

해설: 열역학적 온도의 SI 기본 단위는 켈빈이며 기호는 K이다.

출처: 미국 국립표준기술연구소 NIST — [SP 330 — Section 2](https://www.nist.gov/pml/special-publication-330/sp-330-section-2)

확인 근거: The kelvin 절은 켈빈 K를 열역학적 온도의 SI 단위로 정의한다.

### SCI-03 · 화학·원소

산소(O)의 원자번호는 얼마인가?

1. 6
2. 7
3. 8
4. 16

**정답: 3번 — 8**

해설: 산소의 원자번호는 8이다. 원자번호는 원자핵의 양성자 수를 뜻한다.

출처: 영국 왕립화학회 RSC — [Oxygen — Element information, properties and uses](https://periodic-table.rsc.org/element/8/Oxygen)

확인 근거: Fact box의 Atomic number는 8이며, 용어 설명은 원자번호를 양성자 수로 정의한다.

### SCI-04 · 화학·원소

원자번호가 1인 원소는 무엇인가?

1. 헬륨
2. 수소
3. 리튬
4. 탄소

**정답: 2번 — 수소**

해설: 수소의 원자번호는 1이다.

출처: 영국 왕립화학회 RSC — [Hydrogen — Element information, properties and uses](https://periodic-table.rsc.org/element/1/hydrogen)

확인 근거: Hydrogen의 Fact box에서 Atomic number 1을 확인했다.

### SCI-05 · 생명·염기

DNA의 일반적인 상보적 염기쌍에서 아데닌(A)과 짝을 이루는 염기는 무엇인가?

1. 구아닌(G)
2. 사이토신(C)
3. 유라실(U)
4. 타이민(T)

**정답: 4번 — 타이민(T)**

해설: DNA에서 아데닌은 타이민과, 사이토신은 구아닌과 짝을 이룬다.

출처: 미국 국립인간게놈연구소 NHGRI — [Deoxyribonucleic Acid (DNA)](https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid-DNA)

확인 근거: Definition은 DNA에서 아데닌과 타이민, 사이토신과 구아닌이 결합한다고 설명한다.

### SCI-06 · 생명·식물

식물의 잎에 녹색을 띠게 하며 광합성에 관여하는 대표적인 색소는 무엇인가?

1. 멜라닌
2. 엽록소
3. 헤모글로빈
4. 케라틴

**정답: 2번 — 엽록소**

해설: 엽록소는 빛을 흡수하며 식물의 녹색을 나타내는 색소이다.

출처: 미국 국립공원관리청 NPS — [Why Do Leaves Change Colors in the Fall](https://www.nps.gov/articles/why-do-leaves-change-in-the-fall.htm)

확인 근거: NPS 본문은 chlorophyll이 햇빛을 흡수하고 식물의 녹색을 만든다고 설명한다.

### SCI-07 · 물리·상변화

1기압에서 순수한 물이 끓는 온도는 섭씨 약 몇 도인가?

1. 0°C
2. 50°C
3. 100°C
4. 200°C

**정답: 3번 — 100°C**

해설: 순수한 물은 1기압에서 약 100°C에 끓는다. 끓는점은 압력과 용질에 따라 달라지므로 조건을 명시했다.

출처: 미국 지질조사국 USGS — [How hot are Yellowstone’s boiling waters? Some are hotter than others](https://www.usgs.gov/observatories/yvo/news/how-hot-are-yellowstones-boiling-waters-some-are-hotter-others)

확인 근거: USGS 본문은 1기압의 해수면 조건에서 순수한 물이 100°C에 끓는다고 설명하며 압력과 용질의 영향을 구분한다.

### SCI-08 · 지구과학·천문

태양에서 가까운 순서로 지구는 몇 번째 행성인가?

1. 첫 번째
2. 두 번째
3. 세 번째
4. 네 번째

**정답: 3번 — 세 번째**

해설: 지구는 태양에서 세 번째 행성이다.

출처: 미국 항공우주국 NASA — [Facts About Earth](https://science.nasa.gov/earth/facts/)

확인 근거: Formation 절은 지구가 태양에서 세 번째 행성임을 명시한다.

### SCI-09 · 지구과학·천문

태양에서 가까운 순서로 다섯 번째 행성은 무엇인가?

1. 화성
2. 목성
3. 토성
4. 해왕성

**정답: 2번 — 목성**

해설: 목성은 태양에서 다섯 번째 행성이다.

출처: 미국 항공우주국 NASA — [Jupiter Facts](https://science.nasa.gov/jupiter/jupiter-facts/)

확인 근거: Formation 절은 목성이 태양에서 다섯 번째 행성이라고 설명한다.

### SCI-10 · 생명·분자 구조

일반적인 DNA 분자의 두 가닥이 서로 감겨 이루는 구조를 무엇이라고 부르는가?

1. 단일 고리
2. 평면 격자
3. 삼중 나선
4. 이중 나선

**정답: 4번 — 이중 나선**

해설: DNA의 대표적인 구조는 두 가닥이 서로 감긴 이중 나선이다. 질문은 일반적인 구조를 대상으로 한다.

출처: 미국 국립인간게놈연구소 NHGRI — [Deoxyribonucleic Acid (DNA)](https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid-DNA)

확인 근거: Definition은 DNA의 두 연결된 가닥이 서로 감긴 형태를 double helix라고 설명한다.

## 지리

### GEO-01 · 아시아

후지산이 있는 나라는 어디인가?

1. 일본
2. 중국
3. 네팔
4. 몽골

**정답: 1번 — 일본**

해설: 후지산은 일본에 있는 산이다.

출처: UNESCO 세계유산센터 — [Fujisan, sacred place and source of artistic inspiration](https://whc.unesco.org/en/list/1418/)

확인 근거: 유산 설명은 후지산을 일본의 상징으로 설명하고 국가 항목을 일본으로 표시한다.

### GEO-02 · 오세아니아

울루루가 있는 나라는 어디인가?

1. 뉴질랜드
2. 호주
3. 캐나다
4. 남아프리카공화국

**정답: 2번 — 호주**

해설: 울루루는 호주 중부에 있는 거대한 바위 지형이다.

출처: UNESCO 세계유산센터 — [Uluru-Kata Tjuta National Park](https://whc.unesco.org/en/list/447/)

확인 근거: 유산 설명은 울루루와 카타추타가 호주 중부의 평원에 위치한다고 명시한다.

### GEO-03 · 아프리카

킬리만자로산이 있는 나라는 어디인가?

1. 이집트
2. 모로코
3. 탄자니아
4. 나이지리아

**정답: 3번 — 탄자니아**

해설: 킬리만자로 국립공원의 국가 항목은 탄자니아이다.

출처: UNESCO 세계유산센터 — [Kilimanjaro National Park](https://whc.unesco.org/en/list/403/)

확인 근거: 유산 페이지의 국가 항목과 지역 항목은 탄자니아와 킬리만자로 지역을 표시한다.

### GEO-04 · 남아메리카

마추픽추 유적이 있는 나라는 어디인가?

1. 칠레
2. 볼리비아
3. 콜롬비아
4. 페루

**정답: 4번 — 페루**

해설: 마추픽추는 페루에 있는 유적이다.

출처: UNESCO 세계유산센터 — [Historic Sanctuary of Machu Picchu](https://whc.unesco.org/en/list/274/)

확인 근거: 유산 페이지의 국가 항목이 Peru이며 관리 설명에서도 페루의 유산으로 설명한다.

### GEO-05 · 섬과 국가

갈라파고스 제도가 속한 나라는 어디인가?

1. 에콰도르
2. 페루
3. 칠레
4. 브라질

**정답: 1번 — 에콰도르**

해설: 갈라파고스 제도는 에콰도르에 속한다.

출처: UNESCO 세계유산센터 — [Galápagos Islands](https://whc.unesco.org/en/list/1/)

확인 근거: 유산 페이지의 국가 항목은 Ecuador이며 갈라파고스주를 위치로 제시한다.

### GEO-06 · 아시아

타지마할이 있는 나라는 어디인가?

1. 파키스탄
2. 인도
3. 이란
4. 튀르키예

**정답: 2번 — 인도**

해설: 타지마할은 인도에 있는 유산이다.

출처: UNESCO 세계유산센터 — [Taj Mahal](https://whc.unesco.org/en/list/252/)

확인 근거: 유산 페이지의 국가 항목은 India이며 위치는 Uttar Pradesh, Agra District이다.

### GEO-07 · 하천과 지형

그랜드캐니언의 형성에 큰 역할을 한 하천은 무엇인가?

1. 아마존강
2. 나일강
3. 콜로라도강
4. 다뉴브강

**정답: 3번 — 콜로라도강**

해설: 그랜드캐니언의 형성에는 콜로라도강의 침식이 큰 역할을 했다.

출처: UNESCO 세계유산센터 — [Grand Canyon National Park](https://whc.unesco.org/en/list/75/)

확인 근거: 유산 설명과 Brief synthesis는 콜로라도강의 침식으로 그랜드캐니언이 형성되었다고 설명한다.

### GEO-08 · 해양

해양 분지의 표면적을 기준으로 세계에서 가장 큰 대양은 무엇인가?

1. 대서양
2. 인도양
3. 북극해
4. 태평양

**정답: 4번 — 태평양**

해설: NOAA는 표면적을 제시하며 태평양을 세계에서 가장 큰 해양 분지로 설명한다.

출처: 미국 해양대기청 NOAA — [What is the largest ocean basin on Earth?](https://oceanservice.noaa.gov/facts/biggestocean.html)

확인 근거: NOAA는 태평양의 면적을 약 1억 6,200만 제곱킬로미터로 제시하며 가장 큰 해양 분지라고 설명한다.

### GEO-09 · 위도

적도의 위도는 몇 도인가?

1. 0°
2. 북위 23.5°
3. 남위 66.5°
4. 북위 90°

**정답: 1번 — 0°**

해설: 적도는 위도 0°를 나타내는 기준선이다.

출처: National Geographic Society — [Equator](https://education.nationalgeographic.org/resource/equator/)

확인 근거: National Geographic의 Equator 설명은 적도의 위도를 0도로 제시한다.

### GEO-10 · 경도의 기준

1884년 국제회의에서 본초자오선의 기준으로 선택한 천문대는 어디인가?

1. 파리 천문대
2. 그리니치 천문대
3. 시드니 천문대
4. 도쿄 천문대

**정답: 2번 — 그리니치 천문대**

해설: 1884년 국제회의는 그리니치 자오선을 공통 기준으로 선택했다. 질문은 역사적 결정에 한정하며 현대 GPS 기준선과 혼동하지 않는다.

출처: Royal Museums Greenwich — [What is the Prime Meridian, and why is it in Greenwich?](https://www.rmg.co.uk/stories/time/what-prime-meridian-why-it-greenwich)

확인 근거: 1884년 회의 설명은 그리니치 자오선의 선택과 Airy Transit Circle의 기준을 설명하며 현대 기준선과의 차이도 다룬다.

## 일반상식

### GEN-01 · 문학

희곡 「로미오와 줄리엣」의 작가는 누구인가?

1. 찰스 디킨스
2. 제인 오스틴
3. 윌리엄 셰익스피어
4. 루이스 캐럴

**정답: 3번 — 윌리엄 셰익스피어**

해설: 「로미오와 줄리엣」은 윌리엄 셰익스피어의 희곡이다.

출처: Project Gutenberg — [Romeo and Juliet by William Shakespeare](https://www.gutenberg.org/ebooks/1513)

확인 근거: 전자책의 About this eBook에서 Title과 Author의 연결을 확인했다. 자동 생성 줄거리 요약은 근거로 쓰지 않았다.

### GEN-02 · 문학

소설 「오만과 편견」의 작가는 누구인가?

1. 제인 오스틴
2. 메리 셸리
3. 샬럿 브론테
4. 버지니아 울프

**정답: 1번 — 제인 오스틴**

해설: 「오만과 편견」은 제인 오스틴의 소설이다.

출처: Project Gutenberg — [Pride and Prejudice by Jane Austen](https://www.gutenberg.org/ebooks/1342)

확인 근거: 전자책의 Title은 Pride and Prejudice, Author는 Austen, Jane이다.

### GEN-03 · 문학

「이상한 나라의 앨리스」의 작가는 누구인가?

1. 마크 트웨인
2. 루이스 캐럴
3. 쥘 베른
4. 빅토르 위고

**정답: 2번 — 루이스 캐럴**

해설: 「이상한 나라의 앨리스」는 루이스 캐럴의 작품이다.

출처: Project Gutenberg — [Alice’s Adventures in Wonderland by Lewis Carroll](https://www.gutenberg.org/ebooks/11)

확인 근거: 전자책의 Title은 Alice’s Adventures in Wonderland, Author는 Carroll, Lewis이다.

### GEN-04 · 문학

소설 「프랑켄슈타인」의 작가는 누구인가?

1. 에밀리 브론테
2. 제인 오스틴
3. 애거서 크리스티
4. 메리 셸리

**정답: 4번 — 메리 셸리**

해설: 「프랑켄슈타인」은 메리 셸리의 소설이다.

출처: Project Gutenberg — [Frankenstein; or, the modern prometheus by Mary Wollstonecraft Shelley](https://www.gutenberg.org/ebooks/84)

확인 근거: 전자책의 Author는 Shelley, Mary Wollstonecraft이며 Title은 Frankenstein이다.

### GEN-05 · 미술

「모나리자」를 그린 화가는 누구인가?

1. 레오나르도 다 빈치
2. 미켈란젤로
3. 라파엘로
4. 산드로 보티첼리

**정답: 1번 — 레오나르도 다 빈치**

해설: 루브르의 작품 설명은 「모나리자」의 화가를 레오나르도 다 빈치로 표시한다.

출처: 루브르 박물관 — [From the Mona Lisa to The Wedding Feast at Cana — The Salle des États](https://www.louvre.fr/en/explore/the-palace/from-the-mona-lisa-to-the-wedding-feast-at-cana)

확인 근거: 루브르 본문과 작품 캡션에서 화가와 작품명의 연결을 확인했다.

### GEN-06 · 미술

1889년 작품 「별이 빛나는 밤」(The Starry Night)의 화가는 누구인가?

1. 클로드 모네
2. 빈센트 반 고흐
3. 폴 세잔
4. 파블로 피카소

**정답: 2번 — 빈센트 반 고흐**

해설: MoMA의 1889년 「별이 빛나는 밤」은 빈센트 반 고흐의 작품이다. 다른 밤 풍경 작품과 구분하기 위해 연도와 원제를 적었다.

출처: 뉴욕 현대미술관 MoMA — [Vincent van Gogh. The Starry Night. 1889](https://www.moma.org/collection/works/79802)

확인 근거: MoMA 작품 페이지 제목이 Vincent van Gogh. The Starry Night. Saint Rémy, June 1889이다.

### GEN-07 · 조각

조각 「생각하는 사람」(The Thinker)의 작가는 누구인가?

1. 도나텔로
2. 알베르토 자코메티
3. 오귀스트 로댕
4. 콘스탄틴 브랑쿠시

**정답: 3번 — 오귀스트 로댕**

해설: 로댕 미술관은 「생각하는 사람」의 작가를 오귀스트 로댕으로 표시한다.

출처: 로댕 미술관 — [The Thinker](https://www.musee-rodin.fr/en/musee/collections/oeuvres/thinker)

확인 근거: 작품 페이지의 작가 항목은 Auguste Rodin이다.

### GEN-08 · 미술

회화 「절규」(The Scream)의 작가는 누구인가?

1. 구스타프 클림트
2. 살바도르 달리
3. 르네 마그리트
4. 에드바르 뭉크

**정답: 4번 — 에드바르 뭉크**

해설: 노르웨이 국립미술관은 「절규」의 작가를 에드바르 뭉크로 표시한다.

출처: 노르웨이 국립미술관 — [Edvard Munch, The Scream](https://www.nasjonalmuseet.no/en/collection/object/NG.M.00939)

확인 근거: 작품 페이지의 Artist 항목은 Edvard Munch이다.

### GEN-09 · 생활·보드게임

표준 체스판의 칸은 모두 몇 개인가?

1. 64개
2. 49개
3. 81개
4. 100개

**정답: 1번 — 64개**

해설: FIDE 규칙 제2.1조의 체스판은 8×8 구조이므로 64칸이다.

출처: 국제체스연맹 FIDE — [FIDE Laws of Chess taking effect from 1 January 2023 — Article 2.1](https://handbook.fide.com/chapter/e012023)

확인 근거: FIDE의 2023년 시행 규칙 제2.1조는 체스판을 8×8, 64칸으로 명시한다. 직접 열기는 실패했지만 공식 도메인 검색 응답에서 조문 본문을 확인했다.

### GEN-10 · 생활·도서

2007년 1월 1일부터 새로 부여하는 ISBN은 몇 자리인가?

1. 10자리
2. 13자리
3. 12자리
4. 16자리

**정답: 2번 — 13자리**

해설: ISBN은 2007년부터 13자리이다. 과거 10자리 ISBN과 혼동하지 않도록 신규 부여 시점을 명시했다.

출처: 국제 ISBN 관리기구 — [What is an ISBN?](https://www.isbn-international.org/index.php/node/10)

확인 근거: 국제 ISBN 관리기구는 2006년 말까지 10자리였고 2007년 1월 1일부터 13자리라고 설명한다.

## 컴퓨터공학

### CS-01 · 프로그래밍

Python 3에서 문자열 바깥의 한 줄 주석을 시작하는 기호는 무엇인가?

1. //
2. /*
3. --
4. #

**정답: 4번 — #**

해설: Python 3의 주석은 문자열 바깥의 #으로 시작해 해당 줄 끝까지 이어진다.

출처: Python Software Foundation — [Python 3 Tutorial — An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)

확인 근거: 튜토리얼 도입부가 # 주석과 문자열 안의 #을 구분해 설명한다.

### CS-02 · 프로그래밍

Python 3에서 표현식 17 % 3의 결과는 무엇인가?

1. 2
2. 3
3. 5
4. 1

**정답: 1번 — 2**

해설: 나머지 연산자 %를 사용하면 17을 3으로 나눈 나머지 2를 얻는다.

출처: Python Software Foundation — [Python 3 Tutorial — An Informal Introduction to Python](https://docs.python.org/3/tutorial/introduction.html)

확인 근거: Numbers 절의 공식 예제에 17 % 3의 결과 2가 제시되어 있다.

### CS-03 · 알고리즘

배열에서 값을 찾는 표준 이진 탐색을 적용하기 위한 데이터 조건은 무엇인가?

1. 모든 값이 서로 달라야 한다
2. 값이 반드시 양수여야 한다
3. 탐색에 사용하는 비교 기준에 따라 정렬되어 있어야 한다
4. 배열 길이가 반드시 짝수여야 한다

**정답: 3번 — 탐색에 사용하는 비교 기준에 따라 정렬되어 있어야 한다**

해설: 표준 이진 탐색은 정렬된 배열에서 가운데 값을 비교하며 탐색 구간을 줄인다.

출처: 미국 국립표준기술연구소 NIST — [Dictionary of Algorithms and Data Structures — binary search](https://xlinux.nist.gov/dads/HTML/binarySearch.html)

확인 근거: NIST의 정의는 정렬된 배열에서 탐색 구간을 반복해서 절반으로 줄이는 탐색이라고 명시한다.

### CS-04 · 알고리즘

배열이나 리스트의 항목을 하나씩 차례로 확인하는 탐색은 무엇인가?

1. 이진 탐색
2. 선형 탐색
3. 해시 탐색
4. 보간 탐색

**정답: 2번 — 선형 탐색**

해설: 선형 탐색은 항목을 하나씩 확인하는 방식이다.

출처: 미국 국립표준기술연구소 NIST — [Dictionary of Algorithms and Data Structures — linear search](https://xlinux.nist.gov/dads/HTML/linearSearch.html)

확인 근거: NIST의 정의는 배열이나 리스트의 항목을 한 번에 하나씩 확인하는 탐색이며 sequential search라고도 부른다고 설명한다.

### CS-05 · 자료구조

마지막에 넣은 항목을 가장 먼저 꺼내는 LIFO 자료구조는 무엇인가?

1. 큐
2. 집합
3. 스택
4. 그래프

**정답: 3번 — 스택**

해설: 스택은 후입선출(LIFO) 방식이다.

출처: Python Software Foundation — [Python 3 Tutorial — Data Structures, 5.1.1–5.1.2](https://docs.python.org/3/tutorial/datastructures.html)

확인 근거: 5.1.1 Using Lists as Stacks는 마지막으로 넣은 항목을 먼저 꺼내는 동작을 설명한다.

### CS-06 · 자료구조

먼저 넣은 항목을 가장 먼저 꺼내는 FIFO 자료구조는 무엇인가?

1. 스택
2. 트리
3. 집합
4. 큐

**정답: 4번 — 큐**

해설: 큐는 선입선출(FIFO) 방식이다. 우선순위 큐는 이 질문의 대상이 아니다.

출처: Python Software Foundation — [Python 3 Tutorial — Data Structures, 5.1.1–5.1.2](https://docs.python.org/3/tutorial/datastructures.html)

확인 근거: 5.1.2 Using Lists as Queues는 먼저 넣은 항목을 먼저 꺼내는 동작을 설명한다.

### CS-07 · 운영체제

Linux에서 getpid()가 반환하는 것은 무엇인가?

1. 호출한 프로세스의 프로세스 ID
2. 부모 프로세스의 프로세스 ID
3. 현재 스레드의 우선순위
4. 사용 가능한 메모리 용량

**정답: 1번 — 호출한 프로세스의 프로세스 ID**

해설: getpid()는 호출 프로세스의 PID를 반환한다. 부모 PID를 반환하는 getppid()와 구분한다.

출처: Linux man-pages 프로젝트 — [getpid(2) — Linux manual page](https://man7.org/linux/man-pages/man2/getpid.2.html)

확인 근거: DESCRIPTION은 getpid()가 호출 프로세스의 process ID를 반환한다고 명시한다.

### CS-08 · 운영체제

Linux에서 fork()의 기본 역할은 무엇인가?

1. 파일을 삭제한다
2. 호출한 프로세스를 복제해 자식 프로세스를 만든다
3. 운영체제를 재부팅한다
4. 프로세스 이름만 변경한다

**정답: 2번 — 호출한 프로세스를 복제해 자식 프로세스를 만든다**

해설: fork()는 호출 프로세스를 복제하여 새로운 자식 프로세스를 만든다.

출처: Linux man-pages 프로젝트 — [fork(2) — Linux manual page](https://man7.org/linux/man-pages/man2/fork.2.html)

확인 근거: DESCRIPTION은 fork()가 호출 프로세스를 복제하여 새 프로세스를 만들며 이를 child process라고 부른다고 설명한다.

### CS-09 · 네트워크

HTTP 상태 코드 404의 표준 명칭은 무엇인가?

1. Bad Request
2. Forbidden
3. Not Found
4. Internal Server Error

**정답: 3번 — Not Found**

해설: 404의 명칭은 Not Found이다. 리소스의 현재 표현을 찾지 못했거나 존재를 공개하지 않을 때 쓰며 영구 삭제만을 의미하지 않는다.

출처: IETF / RFC Editor — [RFC 9110 — HTTP Semantics, 15.5.5](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5)

확인 근거: RFC 9110 제15.5.5절의 제목은 404 Not Found이며 존재를 공개하지 않는 경우와 일시적·영구적 여부의 한계도 설명한다.

### CS-10 · 네트워크

DNS 리졸버의 대표적인 기능 중 하나는 무엇인가?

1. 모든 파일의 바이러스를 제거한다
2. 모든 통신을 자동으로 암호화한다
3. 인터넷 전송 속도를 무조건 높인다
4. 호스트 이름에 대응하는 호스트 주소를 조회한다

**정답: 4번 — 호스트 이름에 대응하는 호스트 주소를 조회한다**

해설: DNS 리졸버의 대표 기능에는 호스트 이름에서 호스트 주소를 찾는 기능이 있다. DNS가 주소 정보만 저장한다는 뜻은 아니다.

출처: IETF / RFC Editor — [RFC 1034 — Domain Names: Concepts and Facilities, 5.2.1](https://www.rfc-editor.org/rfc/rfc1034.html#section-5.2.1)

확인 근거: RFC 1034 제5.2.1절은 대표 기능으로 호스트 이름에서 호스트 주소로의 변환을 제시한다.

## 파일 구조 검증 결과

2026-10-01에 저장된 JSON을 다시 읽어 확인했다. 총 50문제와 분야별 10문제, 컴퓨터공학의 5개 세부 분야별 2문제를 확인했다. ID·질문·각 문제의 보기에는 중복이 없으며, 모든 정답 인덱스가 0~3 범위에 있다. 모든 문제에 해설·출처 제목·기관·HTTPS URL·확인일·확인 근거가 있고, 이 문서의 문제 ID·정답·출처 링크가 JSON과 일치한다.

이 검사는 문제은행 작성 당시 데이터 구조와 두 파일의 일치 여부를 검사한 것이다. 사실의 정확성을 자동으로 판정한 것은 아니다. 이후 게임 동작 검사 결과는 README.md에 별도로 기록했다.
