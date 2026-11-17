// Minimal DOM mocks: this checks state handling, not a real browser or layout.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

function setup(raw, quota = false) {
  const nodes = new Map();
  const node = () => ({
    value: '', textContent: '', hidden: true, checked: false, children: [], listeners: {},
    classList: {toggle() {}},
    addEventListener(event, fn) { this.listeners[event] = fn; },
    replaceChildren(...items) { this.children = items; },
    append(...items) { this.children.push(...items); },
    setAttribute() {},
  });
  const get = (id) => {
    if (!nodes.has(id)) nodes.set(id, node());
    return nodes.get(id);
  };
  const stored = new Map(raw === null ? [] : [['study05.diary.v1', raw]]);
  const context = {
    document: {body: {dataset: {page: 'diary'}}, getElementById: get, createElement: node, querySelector: get},
    localStorage: {
      getItem(key) { return stored.get(key) ?? null; },
      setItem(key, value) { if (quota) throw Error('quota'); stored.set(key, value); },
      removeItem(key) { stored.delete(key); },
    },
    crypto: {randomUUID: () => 'uuid'},
    Option: function () {},
    confirm: () => false,
    fetch: async () => ({ok: true, json: async () => ({emotion: '뿌듯함', message: '<img src=x onerror=alert(1)> 좋은 하루네요.'})}),
  };
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8'), context);
  get('api-key').value = 'test-key';
  get('model').value = 'test-model';
  get('consent').checked = true;
  get('persist').checked = true;
  get('diary-text').value = '오늘 일을 끝냈다.';
  return {get, stored, context, submit: () => get('diary-form').listeners.submit({preventDefault() {}})};
}

(async () => {
  const success = setup(null);
  success.get('input[name="mood"]:checked').value = '지침';
  let requestBody;
  const fetchSuccess = success.context.fetch;
  success.context.fetch = async (url, options) => { requestBody = JSON.parse(options.body); return fetchSuccess(url, options); };
  await success.submit();
  const saved = JSON.parse(success.stored.get('study05.diary.v1'));
  assert.equal(saved.length, 1);
  assert.equal(saved[0].text, '오늘 일을 끝냈다.');
  assert.equal(saved[0].mood, '지침');
  assert.equal(requestBody.mood, '지침');
  assert.match(success.get('diary-date').textContent, /년/);
  assert.equal(JSON.stringify(saved).includes('test-key'), false);
  assert.match(success.get('message').textContent, /<img/);
  assert.equal(success.get('result').hidden, false);

  const broken = setup('{broken');
  await broken.submit();
  assert.equal(broken.stored.get('study05.diary.v1'), '{broken');
  assert.match(broken.get('history-status').textContent, /기록을 저장하지 못/);
  assert.equal(broken.get('result').hidden, false);

  const original = JSON.stringify([{id: 'a', date: new Date().toISOString(), text: '이전 기록', emotion: '평온', message: '좋아요'}]);
  const quota = setup(original, true);
  await quota.submit();
  assert.equal(quota.stored.get('study05.diary.v1'), original);

  const noPersist = setup(null);
  noPersist.get('persist').checked = false;
  await noPersist.submit();
  assert.equal(noPersist.stored.size, 0);

  success.context.fetch = async () => { throw Error('offline'); };
  await success.submit();
  assert.equal(success.get('result').hidden, false);
  assert.match(success.get('status').textContent, /로컬 서버/);

  success.get('clear-history').listeners.click();
  assert.equal(success.stored.size, 1);
  success.context.confirm = () => true;
  success.get('clear-history').listeners.click();
  assert.equal(success.stored.size, 0);
  console.log('Frontend state self-check passed (DOM mocks; not a real browser/layout test).');
})().catch((error) => { console.error(error); process.exitCode = 1; });
