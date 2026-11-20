// Gentle daily prompts (shown as guidance only, never inserted into the diary).
const DAILY_QUESTIONS = [
  '오늘 가장 오래 머문 장소는 어디였나요?',
  '오늘 누군가에게 고마웠던 순간이 있었나요?',
  '오늘 처음 해 본 일이 있다면 무엇인가요?',
  '오늘 들은 말 중 기억에 남는 한마디는?',
  '오늘 먹은 것 중 가장 기억나는 음식은?',
  '오늘 하루를 한 장면으로 남긴다면 어떤 모습일까요?',
  '오늘 미뤄 둔 일과 해낸 일은 무엇인가요?',
  '요즘 자주 떠올리는 사람은 누구인가요?',
  '오늘 창밖이나 길에서 본 것 중 기억나는 것은?',
  '오늘 나를 웃게 한 일이 있었나요?',
  '오늘 배운 것이나 새로 알게 된 것은?',
  '오늘 가장 조용했던 순간은 언제였나요?',
  '지금 가장 기다리고 있는 일은 무엇인가요?',
  '오늘 들었던 노래나 소리가 있나요?',
  '오늘 내가 나에게 해 주고 싶은 말은?',
  '오늘 걸었던 길은 어땠나요?',
  '요즘 아끼는 물건 하나를 꼽는다면?',
  '오늘 누구와 가장 많이 이야기했나요?',
  '오늘 날씨는 내 하루에 어떤 영향을 줬나요?',
  '1년 뒤의 내가 오늘을 기억한다면 무엇일까요?',
  '오늘 예상과 다르게 흘러간 일이 있었나요?',
  '오늘 손으로 한 일 중 기억나는 것은?',
  '요즘 마음에 걸리는 일이 있다면 무엇인가요?',
  '오늘 가장 편안했던 시간은 언제였나요?',
  '오늘 읽거나 본 것 중 떠오르는 것은?',
  '오늘 나는 어떤 결정을 했나요?',
  '오늘 누군가를 도왔거나 도움을 받았나요?',
  '오늘 하루의 시작은 어땠나요?',
  '오늘 하루의 끝은 어땠나요?',
  '지금 내 책상이나 방에는 무엇이 보이나요?',
  '오늘을 한 단어로 적는다면 무엇인가요?'
];

class DiaryApp {
  constructor() {
    this.startYear = 2024;
    this.selectedYear = 2024;
    this.selectedMonth = 10;
    this.selectedDate = 17;
    this.dirtyFlags = {};
    this.requestInProgress = false;
    this.requestGenerations = {};
    this.unsavedData = {};
    this.draftConflicts = {};
    this.entries = {};
    this.imageConfigured = false;
    this.init();
  }

  async init() {
    const today = this.koreanToday();
    document.getElementById('select-start-year').replaceChildren(...Array.from({length:198}, (_, i) => new Option(`${1900+i} — ${1902+i}`, 1900+i)));
    await this.loadSettings();
    
    this.selectedMonth = today.getMonth();
    this.selectedDate = today.getDate();
    this.selectedYear = this.getBaseYear(today);
    
    this.setupEventListeners();
    this.renderCalendar();
    this.updateDateDisplay();
    this.renderDiarySections();
    this.loadDiarySections();
    
    window.addEventListener('beforeunload', (e) => {
      if (this.hasPendingChanges()) {
        e.preventDefault();
        e.returnValue = '';
      }
    });
  }

  async loadSettings() {
    try {
      const response = await fetch('/api/settings');
      if (!response.ok) throw new Error('Failed to load settings');
      const data = await response.json();
      this.startYear = data.start_year || 2024;
      this.imageConfigured = data.image_api && data.image_api.configured === true;
      const consent = document.getElementById('image-consent');
      consent.disabled = !this.imageConfigured;
      document.getElementById('image-api-status').textContent = this.imageConfigured
        ? '키가 설정되어 있어요. 실제 연결은 첫 생성 때 확인합니다.'
        : '학교 API 키를 로컬 설정 파일에 입력해 주세요. 일기 저장은 연결 없이도 가능합니다.';
      this.setupMusic(data.music);
      this.setupNarration(data.narration);
      this.updateStartYearSelect();
    } catch (error) {
      console.error('Settings load error:', error);
      this.startYear = 2024;
    }
  }

  // Fills both music selectors from the server's track list and shows each track's required credit.
  setupMusic(music) {
    if (!music || !Array.isArray(music.tracks)) return;
    this.musicTracks = Object.fromEntries(music.tracks.map(track => [track.id, track]));
    for (const id of ['shorts-music', 'three-year-music']) {
      const select = document.getElementById(id);
      select.replaceChildren(...music.tracks.map(track => new Option(track.label, track.id)));
      select.value = music.default;
      const credit = document.getElementById(id + '-credit');
      const show = () => { credit.textContent = this.musicCredit(select.value); };
      select.addEventListener('change', show);
      show();
    }
  }

  // Narration options appear only when the local voice model is installed (never in the online demo).
  setupNarration(info) {
    this.narrationAvailable = !!info && info.available === true;
    this.narrationCredit = this.narrationAvailable && typeof info.credit === 'string' ? info.credit : '';
    const options = typeof document.querySelectorAll === 'function' ? document.querySelectorAll('.narration-option') : [];
    for (const option of options) option.hidden = !this.narrationAvailable;
  }

  wantsNarration(id) {
    const box = document.getElementById(id);
    return this.narrationAvailable === true && !!box && box.checked === true;
  }

  musicCredit(id) {
    const track = this.musicTracks && this.musicTracks[id];
    return track ? `음악: ${track.credit}` : '';
  }

  selectedMusic(id) {
    const select = document.getElementById(id);
    return select && select.value ? select.value : undefined;
  }

  updateStartYearSelect() {
    const select = document.getElementById('select-start-year');
    select.value = this.startYear.toString();
  }

  setupEventListeners() {
    document.getElementById('three-year-video').addEventListener('click', () => this.makeThreeYearVideo());
    document.getElementById('past-banner-read').addEventListener('click', () => this.readPastEntry());
    document.getElementById('close-videos').addEventListener('click', () => document.getElementById('dialog-videos').close());
    document.getElementById('dialog-videos').addEventListener('close', () => document.querySelectorAll('#saved-videos video').forEach(v => v.pause()));
    document.getElementById('make-scene-images').addEventListener('click', () => this.prepareSceneImages());
    document.getElementById('calendar-year').addEventListener('change', (event) => {
      this.selectedYear = Number(event.target.value);
      this.renderCalendar();
    });
    document.getElementById('dialog-shorts').addEventListener('close', () => document.getElementById('shorts-video').pause());
    document.getElementById('retry-story').addEventListener('click', () => this.prepareShortsStory());
    document.getElementById('shorts-captions').addEventListener('input', () => this.renderShortsStory());
    document.getElementById('make-shorts').addEventListener('click', () => this.makeShorts());
    document.getElementById('close-shorts').addEventListener('click', () => document.getElementById('dialog-shorts').close());
    document.getElementById('btn-prev-month').addEventListener('click', () => this.previousMonth());
    document.getElementById('btn-next-month').addEventListener('click', () => this.nextMonth());
    document.getElementById('btn-prev-day').addEventListener('click', () => this.previousDay());
    document.getElementById('btn-next-day').addEventListener('click', () => this.nextDay());
    document.getElementById('btn-today').addEventListener('click', () => this.goToday());
    document.getElementById('btn-load-demo').addEventListener('click', () => this.loadDemoData());
    document.getElementById('select-start-year').addEventListener('change', (e) => this.changeStartYear(e));
    document.getElementById('btn-close-image').addEventListener('click', () => this.closeImageDialog());
    document.getElementById('btn-close-info').addEventListener('click', () => this.closeInfoDialog());
    document.getElementById('dialog-image').addEventListener('click', (e) => {
      if (e.target.id === 'dialog-image') this.closeImageDialog();
    });
    document.getElementById('dialog-info').addEventListener('click', (e) => {
      if (e.target.id === 'dialog-info') this.closeInfoDialog();
    });
  }

  getBaseYear(today) {
    const currentYear = today.getFullYear();
    if (currentYear >= this.startYear && currentYear <= this.startYear + 2) {
      return currentYear;
    }
    return this.startYear;
  }

  isLeapYear(year) {
    return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
  }

  getSeason(month) {
    if (month >= 2 && month <= 4) return 'spring';
    if (month >= 5 && month <= 7) return 'summer';
    if (month >= 8 && month <= 10) return 'autumn';
    return 'winter';
  }

  renderCalendar() {
    const year = this.selectedYear, month = this.selectedMonth;
    document.getElementById('display-month').textContent = `${year}년 ${month + 1}월`;
    const yearSelect = document.getElementById('calendar-year');
    yearSelect.replaceChildren(...Array.from({length: 3}, (_, i) => {
      const value = this.startYear + i;
      return new Option(`${value}년 달력`, value);
    }));
    yearSelect.value = String(year);
    const tbody = document.getElementById('calendar-body');
    tbody.replaceChildren();
    const first = new Date(year, month, 1).getDay();
    const count = new Date(year, month + 1, 0).getDate();
    for (let index = 0; index < Math.ceil((first + count) / 7) * 7; index++) {
      if (index % 7 === 0) tbody.appendChild(document.createElement('tr'));
      const cell = document.createElement('td');
      const day = index - first + 1;
      if (day > 0 && day <= count) {
        const button = document.createElement('button');
        button.textContent = day;
        button.className = 'calendar-day';
        button.setAttribute('aria-label', `${year}년 ${month + 1}월 ${day}일`);
        if (day === this.selectedDate) {
          button.classList.add('selected');
          button.setAttribute('aria-current', 'date');
        }
        button.addEventListener('click', () => this.selectDate(day));
        cell.appendChild(button);
      }
      tbody.lastElementChild.appendChild(cell);
    }
  }

  selectDate(day) {
    if (this.requestInProgress) return;
    if (this.hasPendingChanges()) {
      if (!confirm('저장되지 않은 변경 사항이 있습니다. 계속 진행하시겠습니까?')) {
        this.renderCalendar();
        return;
      }
    }
    
    this.selectedDate = day;
    this.renderCalendar();
    this.updateDateDisplay();
    this.loadDiarySections();
  }

  previousMonth() {
    this.moveMonth(-1);
  }

  nextMonth() {
    this.moveMonth(1);
  }

  previousDay() {
    if (this.requestInProgress) return;
    if (this.hasPendingChanges()) {
      if (!confirm('저장되지 않은 변경 사항이 있습니다. 계속 진행하시겠습니까?')) {
        return;
      }
    }
    
    const validYear = [this.selectedYear, this.startYear, this.startYear + 1, this.startYear + 2]
      .find(year => new Date(year, this.selectedMonth, this.selectedDate).getMonth() === this.selectedMonth);
    const referenceYear = validYear === undefined ? 2000 : validYear;
    const date = new Date(referenceYear, this.selectedMonth, this.selectedDate - 1);
    this.selectedYear = (validYear === undefined ? this.selectedYear : validYear) + date.getFullYear() - referenceYear;
    this.selectedMonth = date.getMonth();
    this.selectedDate = date.getDate();
    this.renderCalendar();
    this.updateDateDisplay();
    this.loadDiarySections();
  }

  nextDay() {
    if (this.requestInProgress) return;
    if (this.hasPendingChanges()) {
      if (!confirm('저장되지 않은 변경 사항이 있습니다. 계속 진행하시겠습니까?')) {
        return;
      }
    }
    
    const validYear = [this.selectedYear, this.startYear, this.startYear + 1, this.startYear + 2]
      .find(year => new Date(year, this.selectedMonth, this.selectedDate).getMonth() === this.selectedMonth);
    const referenceYear = validYear === undefined ? 2000 : validYear;
    const date = new Date(referenceYear, this.selectedMonth, this.selectedDate + 1);
    this.selectedYear = (validYear === undefined ? this.selectedYear : validYear) + date.getFullYear() - referenceYear;
    this.selectedMonth = date.getMonth();
    this.selectedDate = date.getDate();
    this.renderCalendar();
    this.updateDateDisplay();
    this.loadDiarySections();
  }

  goToday() {
    if (this.requestInProgress) return;
    if (this.hasPendingChanges()) {
      if (!confirm('저장되지 않은 변경 사항이 있습니다. 계속 진행하시겠습니까?')) {
        return;
      }
    }
    
    const today = this.koreanToday();
    this.selectedYear = this.getBaseYear(today);
    this.selectedMonth = today.getMonth();
    this.selectedDate = today.getDate();
    this.renderCalendar();
    this.updateDateDisplay();
    this.loadDiarySections();
  }

  updateDateDisplay() {
    const monthNames = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const dateStr = `${monthNames[this.selectedMonth]} ${this.selectedDate}일`;
    document.getElementById('display-date').textContent = dateStr;
    document.querySelector('.content-area').dataset.season = this.getSeason(this.selectedMonth);
    document.getElementById('daily-question').textContent = this.dailyQuestion(this.selectedMonth, this.selectedDate);
  }

  // The same month/day gets the same question every year, so three years of answers line up.
  dailyQuestion(month, day) {
    const index = Math.round((Date.UTC(2024, month, day) - Date.UTC(2024, 0, 1)) / 86400000);
    return DAILY_QUESTIONS[index % DAILY_QUESTIONS.length];
  }

  // Invites reading earlier years first when the latest writable year is still empty. No counts or scores.
  updatePastBanner() {
    const banner = document.getElementById('past-banner');
    if (!banner) return;
    const today = this.koreanToday();
    const years = [0, 1, 2].map(offset => this.startYear + offset).filter(year =>
      !(this.selectedMonth === 1 && this.selectedDate === 29 && !this.isLeapYear(year))
      && new Date(year, this.selectedMonth, this.selectedDate) <= today);
    const entryOf = year => {
      const entry = this.entries[year];
      return entry && entry.date === this.getDateString(year, this.selectedMonth, this.selectedDate) ? entry : null;
    };
    const latest = years[years.length - 1];
    const past = years.slice(0, -1).filter(year => entryOf(year) && entryOf(year).content);
    const latestEntry = latest === undefined ? null : entryOf(latest);
    if (!past.length || !latestEntry || latestEntry.content) {
      banner.hidden = true;
      return;
    }
    document.getElementById('past-banner-text').textContent = `${past.join('·')}년의 오늘이 기다리고 있어요. ${latest}년의 오늘은 아직 비어 있어요.`;
    this.pastBannerYear = past[0];
    banner.hidden = false;
  }

  readPastEntry() {
    const section = document.querySelector(`.diary-section[data-year="${this.pastBannerYear}"]`);
    if (!section) return;
    section.scrollIntoView({behavior: 'smooth', block: 'start'});
    section.querySelector('textarea').focus({preventScroll: true});
  }

  renderDiarySections() {
    const container = document.getElementById('diary-sections');
    container.innerHTML = '';
    this.entries = {};
    
    for (let offset = 0; offset < 3; offset++) {
      const year = this.startYear + offset;
      const section = this.createDiarySection(year);
      container.appendChild(section);
    }
  }

  createDiarySection(year) {
    const section = document.createElement('div');
    section.className = `diary-section season-${this.getSeason(this.selectedMonth)}`;
    section.dataset.year = year;
    
    const header = document.createElement('div');
    header.className = 'section-header';
    header.innerHTML = `
      <span class="year-title">${year}</span>
      <span class="weekday-text">-</span>
    `;
    section.appendChild(header);
    
    const wrapper = document.createElement('div');
    wrapper.className = 'section-textarea-wrapper';
    
    const textarea = document.createElement('textarea');
    textarea.className = 'section-textarea';
    textarea.dataset.year = year;
    textarea.placeholder = '여기에 기록하세요';
    textarea.maxLength = 10000;
    textarea.setAttribute('aria-label', `${year}년 일기`);
    textarea.addEventListener('input', (e) => this.onTextareaInput(year, e));
    wrapper.appendChild(textarea);
    
    const status = document.createElement('div');
    status.className = 'section-status';
    status.id = `status-${year}`;
    status.setAttribute('aria-live', 'polite');
    wrapper.appendChild(status);
    
    const buttons = document.createElement('div');
    buttons.className = 'section-buttons';
    
    const saveBtn = document.createElement('button');
    saveBtn.className = 'btn-save';
    saveBtn.textContent = '저장';
    saveBtn.dataset.year = year;
    saveBtn.addEventListener('click', () => this.saveDiary(year));
    buttons.appendChild(saveBtn);
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'btn-delete';
    deleteBtn.textContent = '삭제';
    deleteBtn.dataset.year = year;
    deleteBtn.addEventListener('click', () => this.deleteDiary(year));
    buttons.appendChild(deleteBtn);
    
    wrapper.appendChild(buttons);
    section.appendChild(wrapper);
    
    const imageWrapper = document.createElement('div');
    imageWrapper.className = 'section-image-wrapper';
    
    const img = document.createElement('img');
    img.className = 'section-image';
    img.id = `image-${year}`;
    img.alt = `${year}년 일기 수채화 — 시연용 이미지`;
    img.tabIndex = 0;
    img.setAttribute('role', 'button');
    img.setAttribute('aria-label', `${year}년 수채화 크게 보기`);
    img.addEventListener('keydown', event => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); this.showImageDialog(img.src);}});
    img.addEventListener('error', () => {img.style.display = 'none'; document.getElementById(`image-status-${year}`).textContent = '그림을 불러오지 못했습니다.';});
    img.style.display = 'none';
    img.addEventListener('click', (e) => this.showImageDialog(e.target.src));
    imageWrapper.appendChild(img);
    
    const imgStatus = document.createElement('div');
    imgStatus.className = 'image-status';
    imgStatus.id = `image-status-${year}`;
    imageWrapper.appendChild(imgStatus);
    const generate = document.createElement('button');
    generate.className = 'btn-generate';
    generate.dataset.year = year;
    generate.textContent = '그림 만들기';
    generate.disabled = true;
    generate.addEventListener('click', () => this.generateImage(year));
    imageWrapper.appendChild(generate);
    const shorts = document.createElement('button');
    shorts.className = 'btn-shorts';
    shorts.dataset.year = year;
    shorts.textContent = '쇼츠 만들기';
    shorts.disabled = true;
    shorts.addEventListener('click', () => this.showShortsDialog(year));
    imageWrapper.appendChild(shorts);
    const saved = document.createElement('button');
    saved.className = 'btn-history';
    saved.textContent = '보관한 쇼츠';
    saved.addEventListener('click', () => this.showSavedVideos(this.getDateString(year, this.selectedMonth, this.selectedDate)));
    imageWrapper.appendChild(saved);
    const storyNotice = document.createElement('p');
    storyNotice.className = 'image-status';
    storyNotice.textContent = '선택하면 일기를 학교 AI로 보내 이야기를 구성해요. 크레딧이 사용돼요.';
    imageWrapper.appendChild(storyNotice);
    
    section.appendChild(imageWrapper);
    
    return section;
  }

  async loadDiarySections() {
    this.requestInProgress = true;
    this.dirtyFlags = {};
    try {
      await Promise.all(Array.from({length: 3}, (_, offset) => {
        const year = this.startYear + offset;
        return this.loadDiary(year, this.getDateString(year, this.selectedMonth, this.selectedDate));
      }));
      this.updatePastBanner();
    } finally {
      this.requestInProgress = false;
    }
  }

  async loadDiary(year, dateStr) {
    const section = document.querySelector(`.diary-section[data-year="${year}"]`);
    const textarea = section.querySelector('textarea');
    const status = document.getElementById(`status-${year}`);
    const buttons = section.querySelectorAll('.btn-save,.btn-delete,.btn-generate,.btn-shorts');
    const image = document.getElementById(`image-${year}`);
    section.className = `diary-section season-${this.getSeason(this.selectedMonth)}`;
    textarea.disabled = true;
    buttons.forEach(button => button.disabled = true);
    delete this.draftConflicts[year];
    const valid = !(this.selectedMonth === 1 && this.selectedDate === 29 && !this.isLeapYear(year));
    const history = section.querySelector('.btn-history');
    history.disabled = !valid || new Date(year, this.selectedMonth, this.selectedDate) > this.koreanToday();
    section.querySelector('.weekday-text').textContent = valid
      ? ['일요일','월요일','화요일','수요일','목요일','금요일','토요일'][new Date(year, this.selectedMonth, this.selectedDate).getDay()]
      : '—';
    if (!valid || new Date(year, this.selectedMonth, this.selectedDate) > this.koreanToday()) {
      textarea.value = '';
      textarea.placeholder = valid ? '아직 오지 않은 날' : '이 연도에는 2월 29일이 없어요';
      status.className = 'section-status';
      status.textContent = valid ? '아직 오지 않은 날' : '존재하지 않는 날짜';
      image.style.display = 'none';
      document.getElementById(`image-status-${year}`).textContent = '';
      this.unsavedData[year] = '';
      return;
    }
    try {
      const response = await fetch(`/api/diary?date=${dateStr}`);
      if (!response.ok) throw new Error('기록을 읽지 못했습니다.');
      const entry = await response.json();
      if (typeof entry.content !== 'string') throw new Error('기록 형식이 올바르지 않습니다.');
      textarea.value = entry.content;
      textarea.style.height = entry.content.length > 200 ? '300px' : '';
      textarea.placeholder = entry.content ? '이날의 이야기를 적어보세요…' : `오늘의 질문 · ${this.dailyQuestion(this.selectedMonth, this.selectedDate)}`;
      textarea.disabled = false;
      buttons[0].disabled = false;
      buttons[1].disabled = !entry.content;
      this.unsavedData[year] = entry.content;
      this.dirtyFlags[year] = false;
      status.className = entry.is_demo ? 'section-status demo' : 'section-status';
      status.textContent = entry.is_demo ? '시연용 가상 기록' : '';
      document.querySelector(`.btn-delete[data-year="${year}"]`).disabled = !entry.content;
      this.updateImageDisplay(year, entry);
      this.restoreDraft(year, entry, textarea, status);
    } catch (error) {
      status.className = 'section-status error';
      status.textContent = '불러오기 실패. 날짜를 다시 선택해 재시도해 주세요.';
    }
  }

  onTextareaInput(year, event) {
    this.dirtyFlags[year] = event.target.value !== (this.unsavedData[year] || '');
    // Keep the conflicting draft untouched until the user chooses restore or discard.
    if (this.draftConflicts[year]) return;
    try {
      const key = 'diary-draft:' + this.getDateString(year, this.selectedMonth, this.selectedDate);
      if (this.dirtyFlags[year]) localStorage.setItem(key, JSON.stringify({content:event.target.value,base:this.unsavedData[year] || ''}));
      else localStorage.removeItem(key);
      if (typeof document !== 'undefined') document.getElementById(`status-${year}`).textContent = this.dirtyFlags[year] ? '이 브라우저에 임시 저장됨 · 일기 저장은 별도예요' : '';
    } catch (error) {
      if (typeof document !== 'undefined') document.getElementById(`status-${year}`).textContent = '임시 저장을 사용할 수 없어요. 저장 버튼으로 기록해 주세요.';
    }
  }

  restoreDraft(year, entry, textarea, status) {
    delete this.draftConflicts[year];
    try {
      const key = 'diary-draft:' + entry.date;
      const raw = localStorage.getItem(key);
      if (!raw) return;
      const draft = JSON.parse(raw);
      if (typeof draft.content !== 'string' || draft.content.length > 10000) return;
      if (draft.content === entry.content) {localStorage.removeItem(key); return;}
      const restore = () => {
        delete this.draftConflicts[year];
        textarea.value = draft.content;
        textarea.style.height = draft.content.length > 200 ? '300px' : '';
        this.dirtyFlags[year] = draft.content !== entry.content;
        try {localStorage.setItem(key, JSON.stringify({content:draft.content,base:entry.content}));} catch (error) { /* The visible text is still restored. */ }
        status.textContent = '임시 저장한 글을 복구했어요. 저장 버튼으로 반영해 주세요.';
      };
      if (draft.base === entry.content) restore();
      else {
        this.draftConflicts[year] = true;
        status.textContent = '저장된 일기와 다른 임시 글이 있어요. 선택하기 전까지 임시 글은 그대로 보관돼요. ';
        const button = document.createElement('button'); button.textContent = '임시 글 복구';
        button.addEventListener('click', restore); status.appendChild(button);
        const discard = document.createElement('button'); discard.textContent = '임시 글 버리기';
        discard.addEventListener('click', () => {
          delete this.draftConflicts[year];
          try {localStorage.removeItem(key);} catch (error) { /* Nothing else to discard. */ }
          status.textContent = '';
          this.onTextareaInput(year, {target:textarea});
        }); status.appendChild(discard);
      }
    } catch (error) {status.textContent = '임시 저장을 확인하지 못했어요. 저장된 일기는 유지돼요.';}
  }

  async saveDiary(year) {
    if (this.requestInProgress) return;
    
    const textarea = document.querySelector(`textarea[data-year="${year}"]`);
    const content = textarea.value.trim();
    const status = document.getElementById(`status-${year}`);
    
    if (!content) {
      status.className = 'section-status error';
      status.textContent = '내용을 입력하세요';
      return;
    }
    
    const dateStr = this.getDateString(year, this.selectedMonth, this.selectedDate);
    this.requestInProgress = true;
    textarea.disabled = true;
    const generation = {};
    this.requestGenerations[year] = generation;
    
    status.className = 'section-status saving';
    status.textContent = '저장 중...';
    
    try {
      const response = await fetch('/api/diary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ date: dateStr, content: content })
      });
      
      if (this.requestGenerations[year] !== generation) return;
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Save failed');
      }
      
      const entry = await response.json();
      this.unsavedData[year] = content;
      this.dirtyFlags[year] = false;
      // An unresolved conflicting draft stays until the user restores or discards it.
      if (!this.draftConflicts[year]) {
        try {localStorage.removeItem('diary-draft:' + dateStr);} catch (error) { /* Browser storage may be disabled. */ }
      }
      
      status.className = 'section-status success';
      status.textContent = '저장됨';
      setTimeout(() => {
        status.className = 'section-status';
        status.textContent = '';
      }, 2000);
      
      document.querySelector(`.btn-delete[data-year="${year}"]`).disabled = !entry.content;
      this.updateImageDisplay(year, entry);
      // A first picture follows the consent setting; replacing an existing one asks each time.
      if (this.imageConfigured && document.getElementById('image-consent').checked
          && (!entry.image_path || (entry.image_stale && confirm('수정한 일기로 새 수채화를 만들까요? 약 15크레딧이 사용돼요. 취소해도 일기는 저장됐어요.')))) {
        await this.requestImage(year, entry, false);
      }
    } catch (error) {
      if (this.requestGenerations[year] !== generation) return;
      status.className = 'section-status error';
      status.textContent = error.message || '저장 실패';
    } finally {
      this.requestInProgress = false;
      textarea.disabled = false;
    }
  }

  updateImageDisplay(year, entry) {
    this.entries[year] = entry;
    if (document.getElementById('past-banner')) this.updatePastBanner();
    document.querySelector(`.btn-shorts[data-year="${year}"]`).disabled = !entry.content;
    const img = document.getElementById(`image-${year}`);
    const status = document.getElementById(`image-status-${year}`);
    const button = document.querySelector(`.btn-generate[data-year="${year}"]`);
    button.disabled = !this.imageConfigured || !entry.content;
    button.textContent = entry.image_path ? '그림 다시 만들기' : '그림 만들기';
    status.className = 'image-status';
    if (entry.image_path) {
      img.src = entry.image_path;
      img.alt = `${year}년 일기를 바탕으로 만든 수채화`;
      img.style.display = 'block';
      if (entry.image_stale) {
        status.classList.add('stale');
        status.textContent = entry.is_demo && entry.image_path.startsWith('/assets/') ? '참고용 시연 그림 · 새 일기의 실제 생성 확인 전' : '이전 내용으로 만든 그림';
      } else {
        status.textContent = entry.image_path.startsWith('/media/') ? '저장된 수채화' : '시연용 수채화';
      }
    } else {
      img.style.display = 'none';
      status.textContent = this.imageConfigured ? '저장한 일기로 수채화를 만들 수 있어요.' : '학교 API 연결 후 수채화를 만들 수 있어요.';
    }
  }

  async generateImage(year) {
    if (this.requestInProgress || !this.imageConfigured) return;
    if (this.dirtyFlags[year]) {
      this.showInfoDialog('먼저 일기를 저장해 주세요', '지금 편집 중인 이야기를 저장한 다음 그림을 만들어 주세요.');
      return;
    }
    const consent = document.getElementById('image-consent');
    if (!consent.checked) {
      document.getElementById('image-settings').open = true;
      consent.focus();
      return;
    }
    const entry = this.entries[year];
    if (!entry || !entry.content) return;
    const regenerate = !!entry.image_path && entry.image_path.startsWith('/media/');
    if (regenerate && !confirm('새 그림 생성에는 약 15크레딧이 사용됩니다. 다시 만들까요?')) return;
    this.requestInProgress = true;
    const textarea = document.querySelector(`textarea[data-year="${year}"]`);
    textarea.disabled = true;
    try {
      await this.requestImage(year, entry, regenerate);
    } finally {
      textarea.disabled = false;
      this.requestInProgress = false;
    }
  }

  async requestImage(year, entry, regenerate) {
    const status = document.getElementById(`image-status-${year}`);
    const button = document.querySelector(`.btn-generate[data-year="${year}"]`);
    button.disabled = true;
    status.className = 'image-status';
    status.textContent = '수채화를 만들고 있어요… 일기는 저장되어 있어요.';
    try {
      const response = await fetch('/api/image', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({date:entry.date, content_hash:entry.content_hash, regenerate, consent:true})
      });
      let data;
      try { data = await response.json(); }
      catch { throw new Error('그림 응답을 확인하지 못했습니다. 재시도 전에 학교 사용량을 확인해 주세요.'); }
      if (!response.ok) throw new Error(data.error || '그림을 만들지 못했습니다.');
      if (!data.entry || !data.entry.image_path) throw new Error('완성된 그림을 확인하지 못했습니다.');
      this.updateImageDisplay(year, data.entry);
      if (data.cached) status.textContent = '저장된 수채화를 사용했어요. 추가 생성 없음.';
      else status.textContent = typeof data.credits_charged === 'number'
        ? `수채화가 완성됐어요 · ${data.credits_charged}크레딧 사용`
        : '수채화가 완성됐어요. 정확한 차감량은 학교 사용량에서 확인해 주세요.';
    } catch (error) {
      status.className = 'image-status error';
      status.textContent = `${error.message || '그림 연결에 실패했어요.'} 일기와 이전 그림은 유지됩니다.`;
      button.disabled = false;
      button.textContent = '그림 생성 다시 시도';
    }
  }

  async deleteDiary(year) {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    if (this.requestInProgress) return;
    
    const dateStr = this.getDateString(year, this.selectedMonth, this.selectedDate);
    this.requestInProgress = true;
    
    try {
      const response = await fetch(`/api/diary?date=${dateStr}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Delete failed');
      
      try {localStorage.removeItem('diary-draft:' + dateStr);} catch (error) { /* Keep deletion available without browser storage. */ }
      await this.loadDiary(year, dateStr);
      this.dirtyFlags[year] = false;
    } catch (error) {
      alert('삭제 실패: ' + error.message);
    } finally {
      this.requestInProgress = false;
    }
  }

  async changeStartYear(event) {
    if (this.requestInProgress || !this.confirmNavigation()) {
      this.updateStartYearSelect();
      return;
    }
    const year = Number(event.target.value);
    this.requestInProgress = true;
    try {
      const response = await fetch('/api/settings', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({start_year: year})
      });
      if (!response.ok) throw new Error('설정 저장 실패');
      this.startYear = year;
      this.selectedYear = this.getBaseYear(this.koreanToday());
      this.dirtyFlags = {};
      this.unsavedData = {};
      this.renderCalendar();
      this.renderDiarySections();
      await this.loadDiarySections();
    } catch (error) {
      this.showInfoDialog('설정 저장 실패', '기존 기간과 기록을 유지했습니다. 다시 시도해 주세요.');
      this.updateStartYearSelect();
    } finally {
      this.requestInProgress = false;
    }
  }

  async loadDemoData() {
    if (this.requestInProgress || !this.confirmNavigation()) return;
    this.requestInProgress = true;
    try {
      const response = await fetch('/api/demo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      if (!response.ok) throw new Error('Demo load failed');
      
      const data = await response.json();
      this.startYear = data.start_year;
      this.selectedYear = this.getBaseYear(this.koreanToday());
      this.selectedMonth = data.month - 1;
      this.selectedDate = data.day;
      
      this.dirtyFlags = {};
      this.unsavedData = {};
      
      this.updateStartYearSelect();
      this.renderCalendar();
      this.updateDateDisplay();
      this.renderDiarySections();
      await this.loadDiarySections();
      
      this.showInfoDialog('시연 데이터 로드됨', '2024·2025·2026년 11월 17일의 가상 기록입니다. 기존 기록은 보존했습니다.');
    } catch (error) {
      alert('시연 데이터 로드 실패');
    } finally {
      this.requestInProgress = false;
    }
  }

  async showShortsDialog(year) {
    if (this.requestInProgress) return;
    if (this.dirtyFlags[year]) {
      this.showInfoDialog('먼저 일기를 저장해 주세요', '편집한 내용을 저장한 다음 쇼츠를 만들어 주세요.');
      return;
    }
    const entry = this.entries[year];
    if (!entry || !entry.content) return;
    if (!entry.image_path || entry.image_stale) {
      this.showInfoDialog('먼저 수채화를 준비해 주세요', '이 일기의 최신 내용으로 그림을 만든 다음 쇼츠를 만들 수 있어요.');
      return;
    }
    this.shortsEntry = entry;
    this.sceneImagesReady = false;
    document.getElementById('make-scene-images').disabled = true;
    document.getElementById('scene-previews').replaceChildren();
    document.getElementById('shorts-date').textContent = entry.date + (entry.is_demo ? ' · 시연용 가상 기록' : '');
    document.getElementById('shorts-original').textContent = entry.content;
    document.getElementById('shorts-image').src = entry.image_path;
    document.getElementById('shorts-captions').value = '';
    document.getElementById('shorts-story').replaceChildren();
    document.getElementById('shorts-edit').hidden = true;
    document.getElementById('shorts-edit').open = false;
    document.getElementById('make-shorts').disabled = true;
    document.getElementById('shorts-video').pause();
    document.getElementById('shorts-video').hidden = true;
    document.getElementById('download-shorts').hidden = true;
    document.getElementById('shorts-status').textContent = '';
    document.getElementById('dialog-shorts').showModal();
    await this.prepareShortsStory();
  }

  renderShortsStory() {
    this.sceneImagesReady = false;
    document.getElementById('scene-previews').replaceChildren();
    const story = document.getElementById('shorts-story');
    story.replaceChildren();
    for (const caption of document.getElementById('shorts-captions').value.split('\n').filter(line => line.trim())) {
      const scene = document.createElement('li');
      scene.textContent = caption;
      story.appendChild(scene);
    }
  }

  async prepareShortsStory() {
    if (this.requestInProgress || !this.shortsEntry) return;
    const entry = this.shortsEntry;
    this.requestInProgress = true;
    const retry = document.getElementById('retry-story'); retry.hidden = true;
    const button = document.getElementById('make-shorts'); button.disabled = true;
    document.getElementById('close-shorts').disabled = true;
    const dialog = document.getElementById('dialog-shorts');
    const preventClose = event => event.preventDefault(); dialog.addEventListener('cancel', preventClose);
    const status = document.getElementById('shorts-status');
    status.textContent = '일기를 읽고 그날의 이야기를 구성하고 있어요…';
    try {
      const response = await fetch('/api/shorts/story', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date:entry.date,content_hash:entry.content_hash,consent:true})});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '이야기를 구성하지 못했습니다.');
      if (!Array.isArray(data.captions) || !data.captions.length || data.captions.length > 8 || data.captions.some(line => typeof line !== 'string' || !line.trim() || line.length > 64)) throw new Error('이야기 형식을 확인하지 못했습니다.');
      document.getElementById('shorts-captions').value = data.captions.join('\n');
      this.renderShortsStory();
      document.getElementById('shorts-edit').hidden = false;
      button.disabled = false;
      document.getElementById('make-scene-images').disabled = false;
      const usage = data.cached ? '저장된 이야기 재사용 · 추가 AI 호출 없음' : (data.credits_charged == null ? '차감량은 학교 사용량에서 확인해 주세요.' : `이야기 구성 ${data.credits_charged}크레딧`);
      const notes = [data.shortened ? 'AI 문장이 길어 장면마다 줄였어요. 필요하면 수정해 주세요.' : '', data.edited ? '이전에 수정한 이야기를 불러왔어요.' : '', data.demo ? '시연용으로 미리 작성해 둔 이야기예요(AI 호출 없음).' : ''].filter(Boolean).join(' ');
      status.textContent = `${data.captions.length}개 장면으로 구성했어요. ${usage}${notes ? ' ' + notes : ''}`;
    } catch (error) {
      status.textContent = error.message + ' 원본 일기는 그대로예요. 재시도 전 학교 사용량을 확인해 주세요.';
      retry.hidden = false;
    } finally {
      this.requestInProgress = false;
      document.getElementById('close-shorts').disabled = false;
      dialog.removeEventListener('cancel', preventClose);
    }
  }

  async prepareSceneImages() {
    if (this.requestInProgress || !this.shortsEntry) return;
    const captions = document.getElementById('shorts-captions').value.split('\n').map(s => s.trim()).filter(Boolean);
    const status = document.getElementById('shorts-status');
    if (!captions.length || captions.length > 8 || captions.some(s => s.length > 64)) {status.textContent = '장면 문장을 먼저 확인해 주세요.'; return;}
    const anchors = [...new Set([0, Math.floor((captions.length-1)/2), captions.length-1])].sort((a,b)=>a-b);
    const entry = this.shortsEntry;
    const dialog = document.getElementById('dialog-shorts');
    const preventClose = e => e.preventDefault(); dialog.addEventListener('cancel',preventClose);
    this.requestInProgress = true;
    for (const id of ['make-shorts','make-scene-images','close-shorts','shorts-captions']) document.getElementById(id).disabled = true;
    const previews = document.getElementById('scene-previews'); previews.replaceChildren();
    this.sceneImagesReady = false;
    let credits = 0, unknownCredits = false;
    const post = body => fetch('/api/shorts/scene',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    try {
      status.textContent = '이미 준비된 장면 그림을 확인하고 있어요…';
      let missing = 0;
      for (const index of anchors) {
        const response = await post({date:entry.date,content_hash:entry.content_hash,caption:captions[index],check_only:true});
        const data = await response.json();
        if (!response.ok) throw Object.assign(new Error(data.error || '장면 그림 상태를 확인하지 못했어요.'), {free:true});
        if (!data.cached) missing++;
      }
      if (missing && !this.imageConfigured) throw Object.assign(new Error('학교 API 키를 설정한 뒤 장면 그림을 만들 수 있어요.'), {free:true});
      if (missing && !confirm(`새 장면 그림 ${missing}장을 만들어요. 약 ${missing*15}크레딧이 사용되고 일기와 장면 문장이 학교 API로 전송됩니다. 계속할까요?`)) {
        status.textContent = '장면 그림 준비를 취소했어요. 기존 수채화 한 장으로도 쇼츠를 만들 수 있어요.';
        return;
      }
      for (let i=0;i<anchors.length;i++) {
        status.textContent = `장면 그림 ${i+1}/${anchors.length} 준비 중… 이미 준비된 그림은 추가 생성하지 않아요.`;
        const caption = captions[anchors[i]];
        const response = await post({date:entry.date,content_hash:entry.content_hash,caption,consent:true});
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || '장면 그림을 준비하지 못했어요.');
        if (typeof data.credits_charged === 'number') credits += data.credits_charged;
        else unknownCredits = true;
        const image = document.createElement('img'); image.src = data.url; image.alt = caption; previews.appendChild(image);
      }
      this.sceneImagesReady = true;
      status.textContent = `장면 그림이 준비됐어요. 장면에 따라 그림이 바뀌어요. 이번 요청 ${unknownCredits ? '차감량은 학교 사용량에서 확인해 주세요.' : credits.toFixed(2)+'크레딧'}`;
    } catch (error) {
      const kept = previews.children.length ? ` 준비된 그림 ${previews.children.length}장은 보관했어요.` : '';
      status.textContent = error.message + (error.free ? '' : kept + ' 재시도 전에 학교 사용량을 확인해 주세요.');
    }
    finally {
      this.requestInProgress = false;
      for (const id of ['make-shorts','make-scene-images','close-shorts','shorts-captions']) document.getElementById(id).disabled = false;
      dialog.removeEventListener('cancel',preventClose);
    }
  }

  async showSavedVideos(date) {
    if (this.requestInProgress) return;
    const dialog = document.getElementById('dialog-videos');
    document.getElementById('saved-videos').replaceChildren();
    document.getElementById('videos-status').textContent = '보관한 영상을 확인하고 있어요…';
    dialog.showModal();
    await this.loadSavedVideos(date);
  }

  async loadSavedVideos(date) {
    const container = document.getElementById('saved-videos');
    try {
      const response = await fetch('/api/videos?date='+date);
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '영상을 불러오지 못했어요.');
      container.replaceChildren();
      for (const saved of data.videos) {
        const section = document.createElement('section');
        const title = document.createElement('p');
        title.textContent = `${saved.kind === 'three-year' ? '3년 이야기' : '하루 이야기'} · ${saved.seconds}초 · ${saved.created_at.slice(0,16).replace('T',' ')}${saved.stale ? ' · 수정·삭제 전 일기로 만든 영상' : ''}`;
        const video = document.createElement('video'); video.src = saved.url; video.controls = true; video.playsInline = true; video.preload = 'metadata';
        const link = document.createElement('a'); link.href = saved.url; link.download = '일기_쇼츠.mp4'; link.textContent = 'MP4 저장';
        const credit = document.createElement('p'); credit.className = 'demo-label';
        credit.textContent = (Array.isArray(saved.music) && saved.music.length ? '음악: ' + saved.music.join(' / ') : '음악: AcousticGuitarSample — RyGuy, Public Domain')
          + (typeof saved.voice === 'string' && saved.voice ? ' · ' + saved.voice : '');
        section.append(title,video,link,credit); container.appendChild(section);
      }
      document.getElementById('videos-status').textContent = data.videos.length ? '일기를 바꿔도 완성된 영상은 보관돼요.' : '아직 이 날짜에 만든 영상이 없어요.';
    } catch (error) {document.getElementById('videos-status').textContent = error.message;}
  }

  async makeThreeYearVideo() {
    if (this.requestInProgress) return;
    const entries = Array.from({length:3},(_,i)=>this.entries[this.startYear+i]);
    if (entries.some((e,i)=>this.dirtyFlags[this.startYear+i] || !e || !e.content || !e.image_path || e.image_stale || e.date !== this.getDateString(this.startYear+i,this.selectedMonth,this.selectedDate))) {
      this.showInfoDialog('세 해의 기록을 준비해 주세요','같은 날짜의 세 해 일기를 모두 저장하고 최신 수채화를 만든 다음 연결할 수 있어요.'); return;
    }
    const dialog = document.getElementById('dialog-videos');
    document.getElementById('saved-videos').replaceChildren();
    document.getElementById('videos-status').textContent = '세 해의 시작과 마무리를 연결하고 있어요…';
    dialog.showModal();
    const preventClose=e=>e.preventDefault(); dialog.addEventListener('cancel',preventClose);
    this.requestInProgress = true; document.getElementById('close-videos').disabled = true;
    try {
      const response = await fetch('/api/three-year-video',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({items:entries.map(e=>({date:e.date,content_hash:e.content_hash})),consent:true,music:this.selectedMusic('three-year-music'),narration:this.wantsNarration('three-year-narration')})});
      const data = await response.json();
      if (!response.ok) throw Object.assign(new Error(data.error || '3년 영상을 만들지 못했어요.'), {free: (response.status === 400 || response.status === 409) && data.may_charge !== true});
      await this.loadSavedVideos(entries[0].date);
    } catch (error) {
      // The server marks failures that happened during a story call (may_charge); other 400/409 are free checks.
      document.getElementById('videos-status').textContent = error.message + ' 원본은 유지돼요.' + (error.free ? '' : ' 재시도 전에 학교 사용량을 확인해 주세요.');
    }
    finally {this.requestInProgress = false; document.getElementById('close-videos').disabled = false; dialog.removeEventListener('cancel',preventClose);}
  }

  async makeShorts() {
    if (this.requestInProgress || !this.shortsEntry) return;
    const captions = document.getElementById('shorts-captions').value.split('\n').map(line => line.trim()).filter(Boolean);
    const status = document.getElementById('shorts-status');
    if (!captions.length || captions.length > 8 || captions.some(line => line.length > 64)) {
      status.textContent = '이야기를 먼저 구성해 주세요. 수정한 문장은 장면당 64자 이내로 확인해 주세요.';
      return;
    }
    const entry = this.shortsEntry;
    this.requestInProgress = true;
    const button = document.getElementById('make-shorts'); button.disabled = true;
    document.getElementById('close-shorts').disabled = true;
    document.getElementById('shorts-captions').disabled = true;
    const dialog = document.getElementById('dialog-shorts');
    const preventClose = event => event.preventDefault(); dialog.addEventListener('cancel', preventClose);
    status.textContent = this.wantsNarration('shorts-narration') ? '자막을 목소리로 읽고 그림·음악과 합쳐 쇼츠를 만들고 있어요…' : '그림과 음악, 자막으로 쇼츠를 만들고 있어요…';
    try {
      const response = await fetch('/api/shorts', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({items:[{date:entry.date,content_hash:entry.content_hash,caption:captions[0]}],captions,scene_images:this.sceneImagesReady === true,music:this.selectedMusic('shorts-music'),narration:this.wantsNarration('shorts-narration')})});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || '쇼츠 생성 실패');
      const video = document.getElementById('shorts-video'); video.src = data.url; video.hidden = false;
      const link = document.getElementById('download-shorts'); link.href = data.url; link.hidden = false;
      status.textContent = `${data.seconds}초 쇼츠가 완성됐어요. 재생하거나 MP4로 저장할 수 있어요.`;
    } catch (error) {status.textContent = error.message + ' 원본 일기와 그림은 유지됩니다.';}
    finally {
      this.requestInProgress = false;
      button.disabled = false;
      document.getElementById('close-shorts').disabled = false;
      document.getElementById('shorts-captions').disabled = false;
      dialog.removeEventListener('cancel', preventClose);
    }
  }

  showImageDialog(src) {
    const dialog = document.getElementById('dialog-image');
    const preview = document.getElementById('dialog-image-preview');
    preview.src = src;
    dialog.showModal();
  }

  closeImageDialog() {
    const dialog = document.getElementById('dialog-image');
    dialog.close();
  }

  showInfoDialog(title, message) {
    const dialog = document.getElementById('dialog-info');
    document.getElementById('dialog-title').textContent = title;
    document.getElementById('dialog-message').textContent = message;
    dialog.showModal();
  }

  closeInfoDialog() {
    const dialog = document.getElementById('dialog-info');
    dialog.close();
  }

  getDateString(year, month, date) {
    const monthStr = String(month + 1).padStart(2, '0');
    const dateStr = String(date).padStart(2, '0');
    return `${year}-${monthStr}-${dateStr}`;
  }

  koreanToday() {
    const [year, month, day] = new Intl.DateTimeFormat('en-CA', {timeZone:'Asia/Seoul', year:'numeric', month:'2-digit', day:'2-digit'}).format(new Date()).split('-').map(Number);
    return new Date(year, month - 1, day);
  }

  confirmNavigation() {
    return !this.hasPendingChanges() || confirm('저장하지 않은 내용이 있어요. 내용을 버리고 이동할까요?');
  }

  moveMonth(delta) {
    if (this.requestInProgress || !this.confirmNavigation()) return;
    const next = new Date(this.selectedYear, this.selectedMonth + delta, 1);
    this.selectedYear = next.getFullYear();
    this.selectedMonth = next.getMonth();
    this.selectedDate = Math.min(this.selectedDate, new Date(this.selectedYear, this.selectedMonth + 1, 0).getDate());
    this.renderCalendar();
    this.updateDateDisplay();
    this.loadDiarySections();
  }

  hasPendingChanges() {
    for (const year in this.dirtyFlags) {
      if (this.dirtyFlags[year]) return true;
    }
    return false;
  }
}

const app = new DiaryApp();
