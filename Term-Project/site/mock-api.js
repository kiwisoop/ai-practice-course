// GitHub Pages 온라인 시연판 전용: 서버 API를 브라우저 안에서 흉내 낸다.
// - 일기는 이 브라우저(localStorage)에만 저장한다.
// - 학교 AI(이야기·그림)는 절대 호출하지 않는다. 시연 기록에는 미리 만든 결과를 쓴다.
(() => {
  'use strict';
  const realFetch = window.fetch.bind(window);
  const MEDIA = '../';
  const DIARY = 'static-diary:';
  const VIDEOS = 'static-videos';
  const OFFLINE = '온라인 시연판에서는 학교 AI를 호출하지 않아요(토큰 보호). 내 일기로 만들려면 로컬에서 실행해 주세요.';
  const MUSIC = {
    default: 'bright',
    tracks: [
      {id: 'bright', label: '경쾌한 어쿠스틱 (기본)', credit: 'Redwood Trail — Jason Shaw (audionautix.com), CC BY 3.0'},
      {id: 'warm', label: '따뜻한 어쿠스틱', credit: 'Warm Sunset — MusicLFiles, CC BY 4.0'},
      {id: 'calm', label: '잔잔한 기타', credit: 'Acoustic Meditation — Jason Shaw, CC BY 3.0 US'},
      {id: 'hopeful', label: '희망찬 우쿨렐레', credit: 'Ukulele Rising — Squire Tuck, CC BY 4.0'},
      {id: 'guitar', label: '기존 기타 샘플', credit: 'AcousticGuitarSample — RyGuy, Public Domain'},
    ],
  };
  // 미리 렌더링한 예시 영상 (previews/)
  const DAY_VIDEO = {date: '2024-11-17', url: MEDIA + 'previews/example-day.mp4', seconds: 27,
    music: ['Redwood Trail — Jason Shaw (audionautix.com), CC BY 3.0']};
  const THREE_DATES = ['2024-11-17', '2025-11-17', '2026-11-17'];
  const THREE_VIDEO = {url: MEDIA + 'previews/example-three-year.mp4', seconds: 36.5,
    music: ['Warm Sunset — MusicLFiles, CC BY 4.0', 'Ukulele Rising — Squire Tuck, CC BY 4.0']};
  // 예시 영상의 내레이션은 로컬에서 미리 만든 것. 시연판은 음성을 새로 만들지 않는다.
  const VOICE = 'AI 음성: Supertonic 3 (Supertone, OpenRAIL-M) · F1';

  const read = (key, fallback) => {
    try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; } catch { return fallback; }
  };
  const write = (key, value) => {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
  };
  const json = (status, body) => new Response(JSON.stringify(body), {status, headers: {'Content-Type': 'application/json'}});
  const validDate = s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !isNaN(Date.parse(s + 'T00:00:00Z'))
    && new Date(s + 'T00:00:00Z').toISOString().slice(0, 10) === s;
  const koreanToday = () => new Intl.DateTimeFormat('en-CA', {timeZone: 'Asia/Seoul'}).format(new Date());
  async function sha256(text) {
    if (window.crypto && crypto.subtle) {
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
      return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
    }
    let h = 0; for (const c of text) h = (h * 31 + c.codePointAt(0)) >>> 0; // http 미리보기용 대체값
    return 'x' + h.toString(16);
  }
  function entryFor(date) {
    const saved = read(DIARY + date, null);
    if (!saved) return {date, content: '', content_hash: null, image_path: null, image_content_hash: null, is_demo: false, image_stale: false, updated_at: null};
    return {...saved, image_stale: !!saved.image_path && saved.image_content_hash !== saved.content_hash};
  }
  const now = () => new Date().toISOString();

  async function handle(method, url, body) {
    const path = url.pathname;
    if (path === '/api/settings') {
      if (method === 'POST') {
        const year = body && body.start_year;
        if (!Number.isInteger(year) || year < 1900 || year > 2097) return json(400, {error: '시작 연도를 확인해 주세요.'});
        write('static-start-year', year);
        return json(200, {start_year: year});
      }
      return json(200, {start_year: read('static-start-year', 2024), image_api: {configured: false}, music: MUSIC, static_demo: true});
    }
    if (path === '/api/diary') {
      const date = method === 'POST' ? body && body.date : url.searchParams.get('date');
      if (!validDate(date)) return json(400, {error: '존재하지 않거나 형식이 올바르지 않은 날짜입니다.'});
      if (method === 'GET') return json(200, entryFor(date));
      if (method === 'DELETE') { try { localStorage.removeItem(DIARY + date); } catch { /* 없음 */ } return json(200, {ok: true}); }
      const content = typeof body.content === 'string' ? body.content.trim() : '';
      if (!content || content.length > 10000) return json(400, {error: '1~10000자로 적어 주세요.'});
      if (date > koreanToday()) return json(400, {error: '아직 오지 않은 날에는 쓸 수 없어요.'});
      const old = entryFor(date);
      const saved = {date, content, content_hash: await sha256(content), image_path: old.image_path, image_content_hash: old.image_content_hash,
        is_demo: false, captions: null, updated_at: now()};
      if (!write(DIARY + date, saved)) return json(500, {error: '이 브라우저에 저장할 수 없어요(저장 공간 차단).'});
      return json(200, entryFor(date));
    }
    if (path === '/api/demo') {
      const response = await realFetch('demo_diaries.json');
      const demos = await response.json();
      for (const d of demos) {
        const existing = read(DIARY + d.date, null);
        if (existing && !existing.is_demo) continue; // 직접 쓴 기록은 보존
        const hash = await sha256(d.content);
        write(DIARY + d.date, {date: d.date, content: d.content, content_hash: hash, image_path: MEDIA + d.image_path.replace(/^\//, ''),
          image_content_hash: hash, is_demo: true, captions: d.captions || null, updated_at: now()});
      }
      write('static-start-year', 2024);
      return json(200, {start_year: 2024, month: 11, day: 17});
    }
    if (path === '/api/shorts/story') {
      const entry = entryFor(body.date);
      if (entry.is_demo && entry.content_hash === body.content_hash && Array.isArray(entry.captions))
        return json(200, {captions: entry.captions, cached: true, demo: true});
      return json(409, {error: OFFLINE});
    }
    if (path === '/api/shorts/scene') {
      if (body.check_only) return json(200, {cached: false});
      return json(409, {error: OFFLINE});
    }
    if (path === '/api/shorts') {
      const item = body.items && body.items[0];
      const entry = item ? entryFor(item.date) : null;
      if (!entry || !entry.is_demo || item.date !== DAY_VIDEO.date)
        return json(409, {error: '온라인 시연판에는 2024년 11월 17일 하루 쇼츠만 미리 만들어 두었어요. 영상 합성(FFmpeg)은 로컬 실행에서 동작해요.'});
      const videos = read(VIDEOS, []);
      videos.unshift({kind: 'day', sources: {[item.date]: entry.content_hash}, url: DAY_VIDEO.url, seconds: DAY_VIDEO.seconds, music: DAY_VIDEO.music, voice: VOICE, created_at: now()});
      write(VIDEOS, videos.slice(0, 20));
      return json(200, {url: DAY_VIDEO.url, seconds: DAY_VIDEO.seconds, prerendered: true});
    }
    if (path === '/api/three-year-video') {
      const items = body.items || [];
      const ok = items.length === 3 && items.every((it, i) => it.date === THREE_DATES[i] && entryFor(it.date).is_demo && entryFor(it.date).content_hash === it.content_hash);
      if (!ok) return json(409, {error: '온라인 시연판에는 시연 기록(11월 17일)의 3년 쇼츠만 미리 만들어 두었어요.'});
      const videos = read(VIDEOS, []);
      videos.unshift({kind: 'three-year', sources: Object.fromEntries(items.map(it => [it.date, it.content_hash])), url: THREE_VIDEO.url,
        seconds: THREE_VIDEO.seconds, music: THREE_VIDEO.music, voice: VOICE, created_at: now()});
      write(VIDEOS, videos.slice(0, 20));
      return json(200, {url: THREE_VIDEO.url, seconds: THREE_VIDEO.seconds, prerendered: true});
    }
    if (path === '/api/videos') {
      const date = url.searchParams.get('date');
      const videos = read(VIDEOS, []).filter(v => v.sources && date in v.sources)
        .map(v => ({...v, stale: Object.entries(v.sources).some(([d, h]) => entryFor(d).content_hash !== h)}));
      return json(200, {videos});
    }
    if (path === '/api/image') return json(409, {error: OFFLINE});
    return json(404, {error: '없는 기능이에요.'});
  }

  window.fetch = async (input, init = {}) => {
    const raw = input instanceof Request ? input.url : String(input);
    if (!raw.startsWith('/api/')) return realFetch(input, init);
    const url = new URL(raw, 'https://static.invalid');
    const method = (init.method || 'GET').toUpperCase();
    let body = {};
    try { body = init.body ? JSON.parse(init.body) : {}; } catch { return json(400, {error: '요청 형식 오류'}); }
    return handle(method, url, body);
  };
})();
