# 기본 50문제 최종 출처 재검토

확인일: 2026-11-10. 교재 7주차의 마지막 전체 재검토 단계이다. 50문제의 질문·보기·정답·해설을 읽고, 정답의 핵심 근거를 출처 본문 또는 공식 서지·작품 정보와 대조했다. 정답 변경은 없으며 기본 문제 수와 순서는 유지했다.

## 확인 방식과 수정

- HIS-01: 기존 UNESCO 페이지 접근이 시간 초과되어 국사편찬위원회 본문으로 교체했다.
- HIS-03·HIS-10: 기존 국립민속박물관 연혁 페이지 접근 실패로 UNESCO의 조선 기간 표기와 국사편찬위원회 대한제국 설명으로 각각 교체했다.
- GEN-09: 이전에는 검색 응답으로만 확인했으나 이번에는 FIDE 규칙 본문 제2.1조를 직접 열어 8×8·64칸을 확인했다.
- GEO-01·03·04·05: UNESCO 본문과 국가 항목을 함께 확인했다. GEN-01–04는 Gutenberg의 제목·저자 서지를 확인했으며 자동 생성 줄거리는 근거로 사용하지 않았다.
- CS-01·02·05·06은 Python 공식 문서, CS-03·04는 NIST 알고리즘 사전, CS-07·08은 Linux man-pages, CS-09·10은 RFC 본문을 확인했다.
- 압력 조건, 표면적 비교 기준, 1884년 역사적 자오선 결정, ISBN 신규 부여 시점, 언어·운영체제 범위를 다시 확인했다.

## 문제별 확인 근거

| ID | 확인한 정답 | 근거 | 출처 |
| --- | --- | --- | --- |
| HIS-01 | 세종 | 세종의 1443년 창제와 1446년 반포를 설명하는 본문을 대조했다. | [국사편찬위원회 우리역사넷](https://contents.history.go.kr/front/km/print.do?levelId=km_037_0070_0020_0010&whereStr=) |
| HIS-02 | 왕건 | Korea.net 본문은 고려의 연대를 918~1392년으로 제시하고 창건자를 태조 왕건으로 명시한다. | [문화체육관광부 Korea.net](https://www.korea.net/NewsFocus/Culture/view?articleId=166086) |
| HIS-03 | 1392년 | 본문에서 조선 왕조의 기간을 1392–1910년으로 표시한 부분을 확인했다. | [UNESCO World Heritage Centre](https://whc.unesco.org/en/list/738/) |
| HIS-04 | 신라 | Outstanding Universal Value의 Brief synthesis는 8세기 신라 왕조 아래 조성되었다고 설명한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/736/) |
| HIS-05 | 해인사 | 유산 설명과 Brief synthesis는 해인사의 장경판전이 Tripitaka Koreana 목판을 보관한다고 명시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/737/) |
| HIS-06 | 종묘 | Brief synthesis는 종묘가 조선의 옛 왕과 왕비의 신위를 모시는 사당이라고 설명한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/738/) |
| HIS-07 | 정조 | Brief synthesis는 화성이 조선의 정조에 의해 18세기 말 건설되었다고 명시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/817/) |
| HIS-08 | 공주 | 유산 설명은 웅진을 현재의 공주로, 사비를 현재의 부여로 구분한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/1477/) |
| HIS-09 | 조선 | Brief synthesis는 창덕궁이 조선 왕조의 15세기에 건설되었다고 설명한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/816/) |
| HIS-10 | 1897년 | 첫 본문의 1897년 대한제국 국호 변경과 황제 즉위 설명을 대조했다. 날짜의 일 단위는 질문 범위가 아니다. | [국사편찬위원회 우리역사넷](https://contents.history.go.kr/front/ht/print.do?levelId=ht_003_0010&whereStr=) |
| SCI-01 | 암페어(A) | 본문은 ampere (A)를 전류의 SI 기본 단위로 명시한다. | [미국 국립표준기술연구소 NIST](https://www.nist.gov/si-redefinition/ampere-introduction) |
| SCI-02 | 켈빈(K) | The kelvin 절은 켈빈 K를 열역학적 온도의 SI 단위로 정의한다. | [미국 국립표준기술연구소 NIST](https://www.nist.gov/pml/special-publication-330/sp-330-section-2) |
| SCI-03 | 8 | Fact box의 Atomic number는 8이며, 용어 설명은 원자번호를 양성자 수로 정의한다. | [영국 왕립화학회 RSC](https://periodic-table.rsc.org/element/8/Oxygen) |
| SCI-04 | 수소 | Hydrogen의 Fact box에서 Atomic number 1을 확인했다. | [영국 왕립화학회 RSC](https://periodic-table.rsc.org/element/1/hydrogen) |
| SCI-05 | 타이민(T) | Definition은 DNA에서 아데닌과 타이민, 사이토신과 구아닌이 결합한다고 설명한다. | [미국 국립인간게놈연구소 NHGRI](https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid-DNA) |
| SCI-06 | 엽록소 | NPS 본문은 chlorophyll이 햇빛을 흡수하고 식물의 녹색을 만든다고 설명한다. | [미국 국립공원관리청 NPS](https://www.nps.gov/articles/why-do-leaves-change-in-the-fall.htm) |
| SCI-07 | 100°C | USGS 본문은 1기압의 해수면 조건에서 순수한 물이 100°C에 끓는다고 설명하며 압력과 용질의 영향을 구분한다. | [미국 지질조사국 USGS](https://www.usgs.gov/observatories/yvo/news/how-hot-are-yellowstones-boiling-waters-some-are-hotter-others) |
| SCI-08 | 세 번째 | Formation 절은 지구가 태양에서 세 번째 행성임을 명시한다. | [미국 항공우주국 NASA](https://science.nasa.gov/earth/facts/) |
| SCI-09 | 목성 | Formation 절은 목성이 태양에서 다섯 번째 행성이라고 설명한다. | [미국 항공우주국 NASA](https://science.nasa.gov/jupiter/jupiter-facts/) |
| SCI-10 | 이중 나선 | Definition은 DNA의 두 연결된 가닥이 서로 감긴 형태를 double helix라고 설명한다. | [미국 국립인간게놈연구소 NHGRI](https://www.genome.gov/genetics-glossary/Deoxyribonucleic-Acid-DNA) |
| GEO-01 | 일본 | 유산 설명은 후지산을 일본의 상징으로 설명하고 국가 항목을 일본으로 표시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/1418/) |
| GEO-02 | 호주 | 유산 설명은 울루루와 카타추타가 호주 중부의 평원에 위치한다고 명시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/447/) |
| GEO-03 | 탄자니아 | 유산 페이지의 국가 항목과 지역 항목은 탄자니아와 킬리만자로 지역을 표시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/403/) |
| GEO-04 | 페루 | 유산 페이지의 국가 항목이 Peru이며 관리 설명에서도 페루의 유산으로 설명한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/274/) |
| GEO-05 | 에콰도르 | 유산 페이지의 국가 항목은 Ecuador이며 갈라파고스주를 위치로 제시한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/1/) |
| GEO-06 | 인도 | 유산 페이지의 국가 항목은 India이며 위치는 Uttar Pradesh, Agra District이다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/252/) |
| GEO-07 | 콜로라도강 | 유산 설명과 Brief synthesis는 콜로라도강의 침식으로 그랜드캐니언이 형성되었다고 설명한다. | [UNESCO 세계유산센터](https://whc.unesco.org/en/list/75/) |
| GEO-08 | 태평양 | NOAA는 태평양의 면적을 약 1억 6,200만 제곱킬로미터로 제시하며 가장 큰 해양 분지라고 설명한다. | [미국 해양대기청 NOAA](https://oceanservice.noaa.gov/facts/biggestocean.html) |
| GEO-09 | 0° | National Geographic의 Equator 설명은 적도의 위도를 0도로 제시한다. | [National Geographic Society](https://education.nationalgeographic.org/resource/equator/) |
| GEO-10 | 그리니치 천문대 | 1884년 회의 설명은 그리니치 자오선의 선택과 Airy Transit Circle의 기준을 설명하며 현대 기준선과의 차이도 다룬다. | [Royal Museums Greenwich](https://www.rmg.co.uk/stories/time/what-prime-meridian-why-it-greenwich) |
| GEN-01 | 윌리엄 셰익스피어 | 전자책의 About this eBook에서 Title과 Author의 연결을 확인했다. 자동 생성 줄거리 요약은 근거로 쓰지 않았다. | [Project Gutenberg](https://www.gutenberg.org/ebooks/1513) |
| GEN-02 | 제인 오스틴 | 전자책의 Title은 Pride and Prejudice, Author는 Austen, Jane이다. | [Project Gutenberg](https://www.gutenberg.org/ebooks/1342) |
| GEN-03 | 루이스 캐럴 | 전자책의 Title은 Alice’s Adventures in Wonderland, Author는 Carroll, Lewis이다. | [Project Gutenberg](https://www.gutenberg.org/ebooks/11) |
| GEN-04 | 메리 셸리 | 전자책의 Author는 Shelley, Mary Wollstonecraft이며 Title은 Frankenstein이다. | [Project Gutenberg](https://www.gutenberg.org/ebooks/84) |
| GEN-05 | 레오나르도 다 빈치 | 루브르 본문과 작품 캡션에서 화가와 작품명의 연결을 확인했다. | [루브르 박물관](https://www.louvre.fr/en/explore/the-palace/from-the-mona-lisa-to-the-wedding-feast-at-cana) |
| GEN-06 | 빈센트 반 고흐 | MoMA 작품 페이지 제목이 Vincent van Gogh. The Starry Night. Saint Rémy, June 1889이다. | [뉴욕 현대미술관 MoMA](https://www.moma.org/collection/works/79802) |
| GEN-07 | 오귀스트 로댕 | 작품 페이지의 작가 항목은 Auguste Rodin이다. | [로댕 미술관](https://www.musee-rodin.fr/en/musee/collections/oeuvres/thinker) |
| GEN-08 | 에드바르 뭉크 | 작품 페이지의 Artist 항목은 Edvard Munch이다. | [노르웨이 국립미술관](https://www.nasjonalmuseet.no/en/collection/object/NG.M.00939) |
| GEN-09 | 64개 | FIDE의 2023년 시행 규칙 제2.1조는 체스판을 8×8, 64칸으로 명시한다. 직접 열기는 실패했지만 공식 도메인 검색 응답에서 조문 본문을 확인했다. | [국제체스연맹 FIDE](https://handbook.fide.com/chapter/e012023) |
| GEN-10 | 13자리 | 국제 ISBN 관리기구는 2006년 말까지 10자리였고 2007년 1월 1일부터 13자리라고 설명한다. | [국제 ISBN 관리기구](https://www.isbn-international.org/index.php/node/10) |
| CS-01 | # | 튜토리얼 도입부가 # 주석과 문자열 안의 #을 구분해 설명한다. | [Python Software Foundation](https://docs.python.org/3/tutorial/introduction.html) |
| CS-02 | 2 | Numbers 절의 공식 예제에 17 % 3의 결과 2가 제시되어 있다. | [Python Software Foundation](https://docs.python.org/3/tutorial/introduction.html) |
| CS-03 | 탐색에 사용하는 비교 기준에 따라 정렬되어 있어야 한다 | NIST의 정의는 정렬된 배열에서 탐색 구간을 반복해서 절반으로 줄이는 탐색이라고 명시한다. | [미국 국립표준기술연구소 NIST](https://xlinux.nist.gov/dads/HTML/binarySearch.html) |
| CS-04 | 선형 탐색 | NIST의 정의는 배열이나 리스트의 항목을 한 번에 하나씩 확인하는 탐색이며 sequential search라고도 부른다고 설명한다. | [미국 국립표준기술연구소 NIST](https://xlinux.nist.gov/dads/HTML/linearSearch.html) |
| CS-05 | 스택 | 5.1.1 Using Lists as Stacks는 마지막으로 넣은 항목을 먼저 꺼내는 동작을 설명한다. | [Python Software Foundation](https://docs.python.org/3/tutorial/datastructures.html) |
| CS-06 | 큐 | 5.1.2 Using Lists as Queues는 먼저 넣은 항목을 먼저 꺼내는 동작을 설명한다. | [Python Software Foundation](https://docs.python.org/3/tutorial/datastructures.html) |
| CS-07 | 호출한 프로세스의 프로세스 ID | DESCRIPTION은 getpid()가 호출 프로세스의 process ID를 반환한다고 명시한다. | [Linux man-pages 프로젝트](https://man7.org/linux/man-pages/man2/getpid.2.html) |
| CS-08 | 호출한 프로세스를 복제해 자식 프로세스를 만든다 | DESCRIPTION은 fork()가 호출 프로세스를 복제하여 새 프로세스를 만들며 이를 child process라고 부른다고 설명한다. | [Linux man-pages 프로젝트](https://man7.org/linux/man-pages/man2/fork.2.html) |
| CS-09 | Not Found | RFC 9110 제15.5.5절의 제목은 404 Not Found이며 존재를 공개하지 않는 경우와 일시적·영구적 여부의 한계도 설명한다. | [IETF / RFC Editor](https://www.rfc-editor.org/rfc/rfc9110.html#section-15.5.5) |
| CS-10 | 호스트 이름에 대응하는 호스트 주소를 조회한다 | RFC 1034 제5.2.1절은 대표 기능으로 호스트 이름에서 호스트 주소로의 변환을 제시한다. | [IETF / RFC Editor](https://www.rfc-editor.org/rfc/rfc1034.html#section-5.2.1) |

## 한계

AI가 수행한 출처 대조이다. 별도 사람·독립 검토자·새 대화 검토를 수행한 것으로 기록하지 않는다. 모든 문제에 독립 출처 2개를 적용하지 않았으며 링크와 내용은 이후 바뀔 수 있다. 형식·채점 자동 검사는 사실 검증과 별개이다. 원문을 복사하지 않고 핵심 근거를 요약했다.
