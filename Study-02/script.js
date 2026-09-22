const tasks = [];
let nextTaskId = 1;
let editingTaskId = null;
let focusTaskId = null;
let timerState = "idle";
let timerEndTime = 0;
let timerInterval = null;
let focusCount = 0;
let storageLoadError = "";

const categories = ["업무", "과제", "공부", "취미", "개발", "개인"];
const priorityRanks = {높음: 3, 보통: 2, 낮음: 1};
const defaultFocusDuration = 25;
const taskStorageKey = "kiwibird-tasks";
const backupVersion = 1;
const dailyQuotes = [
  "작은 할 일 하나를 끝내는 것이 가장 좋은 시작이에요.",
  "완벽한 계획보다 오늘의 한 걸음이 더 멀리 데려가요.",
  "잠깐의 집중이 하루의 흐름을 바꿀 수 있어요.",
  "서두르지 않아도 괜찮아요. 멈추지만 않으면 돼요.",
  "해낸 일을 바라보며 다음 한 가지를 시작해 보세요.",
];

const form = document.querySelector("#task-form");
const formTitle = document.querySelector("#task-form-title");
const input = document.querySelector("#task-input");
const categoryInput = document.querySelector("#category-input");
const dueDateInput = document.querySelector("#due-date-input");
const priorityInput = document.querySelector("#priority-input");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const searchInput = document.querySelector("#search-input");
const statusFilter = document.querySelector("#status-filter");
const categoryFilter = document.querySelector("#category-filter");
const sortFilter = document.querySelector("#sort-filter");
const resetFiltersButton = document.querySelector("#reset-filters");
const clearCompletedButton = document.querySelector("#clear-completed");
const list = document.querySelector("#task-list");
const emptyState = document.querySelector("#empty-state");
const emptyTitle = document.querySelector("#empty-title");
const emptyDescription = document.querySelector("#empty-description");
const statusMessage = document.querySelector("#status-message");
const todayCount = document.querySelector("#today-count");
const remainingCount = document.querySelector("#remaining-count");
const completedCount = document.querySelector("#completed-count");
const overdueCount = document.querySelector("#overdue-count");
const overallProgress = document.querySelector("#overall-progress");
const progressLabel = document.querySelector("#progress-label");
const nestScene = document.querySelector("#nest-scene");
const nestArt = document.querySelector("#nest-art");
const nestMessage = document.querySelector("#nest-message");
const categoryProgressList = document.querySelector("#category-progress-list");
const themeToggle = document.querySelector("#theme-toggle");
const focusTask = document.querySelector("#focus-task");
const focusReason = document.querySelector("#focus-reason");
const focusCountDisplay = document.querySelector("#focus-count");
const focusDurationInput = document.querySelector("#focus-duration");
const timerDisplay = document.querySelector("#timer-display");
const timerStartButton = document.querySelector("#timer-start");
const timerPauseButton = document.querySelector("#timer-pause");
const timerResumeButton = document.querySelector("#timer-resume");
const timerStopButton = document.querySelector("#timer-stop");
const focusStatus = document.querySelector("#focus-status");
const quickTimeButtons = [...document.querySelectorAll("[data-minutes]")];
const dailyQuote = document.querySelector("#daily-quote");
const exportButton = document.querySelector("#export-button");
const importFileInput = document.querySelector("#import-file");
const backupStatus = document.querySelector("#backup-status");

const dayInMilliseconds = 86_400_000;
let focusDuration = getStoredNumber("kiwibird-focus-duration", defaultFocusDuration);
let remainingSeconds = focusDuration * 60;

function getStoredNumber(key, fallback) {
  try {
    const value = Number(localStorage.getItem(key));
    return Number.isInteger(value) && value >= 5 && value <= 120 ? value : fallback;
  } catch {
    return fallback;
  }
}

function getStoredTheme() {
  try {
    const theme = localStorage.getItem("kiwibird-theme");
    if (theme === "light" || theme === "dark") return theme;
  } catch {
    // The app still works when browser storage is unavailable.
  }
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function storeSetting(key, value) {
  try {
    localStorage.setItem(key, String(value));
  } catch {
    // Settings remain available for the current session.
  }
}

function getLocalDateString() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getStoredFocusCount() {
  try {
    const value = Number(localStorage.getItem(`kiwibird-focus-count-${getLocalDateString()}`));
    return Number.isInteger(value) && value >= 0 ? value : 0;
  } catch {
    return 0;
  }
}

function isValidDateString(value) {
  if (value === "") return true;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year
    && date.getUTCMonth() === month - 1
    && date.getUTCDate() === day;
}

function isIsoTimestamp(value) {
  if (typeof value !== "string" || Number.isNaN(Date.parse(value))) return false;
  return new Date(value).toISOString() === value;
}

function validateBackup(data) {
  if (!data || typeof data !== "object" || data.version !== backupVersion || !Array.isArray(data.tasks)) {
    throw new Error("Kiwibird 백업 파일 형식이 아니에요.");
  }

  const ids = new Set();
  data.tasks.forEach((task, index) => {
    const number = index + 1;
    if (!task || typeof task !== "object") throw new Error(`${number}번째 할 일 형식이 올바르지 않아요.`);
    if (!Number.isInteger(task.id) || task.id < 1 || ids.has(task.id)) throw new Error(`${number}번째 할 일의 번호가 올바르지 않아요.`);
    if (typeof task.title !== "string" || task.title !== task.title.trim() || task.title.length < 1 || task.title.length > 100) {
      throw new Error(`${number}번째 할 일의 내용이 올바르지 않아요.`);
    }
    if (!categories.includes(task.category)) throw new Error(`${number}번째 할 일의 카테고리가 올바르지 않아요.`);
    if (!isValidDateString(task.dueDate)) throw new Error(`${number}번째 할 일의 마감일이 올바르지 않아요.`);
    if (!(task.priority in priorityRanks)) throw new Error(`${number}번째 할 일의 중요도가 올바르지 않아요.`);
    if (typeof task.completed !== "boolean") throw new Error(`${number}번째 할 일의 완료 상태가 올바르지 않아요.`);
    if (!isIsoTimestamp(task.createdAt) || !isIsoTimestamp(task.updatedAt)) {
      throw new Error(`${number}번째 할 일의 저장 시각이 올바르지 않아요.`);
    }
    ids.add(task.id);
  });

  return data.tasks.map((task) => ({
    id: task.id,
    title: task.title,
    category: task.category,
    dueDate: task.dueDate,
    priority: task.priority,
    completed: task.completed,
    createdAt: task.createdAt,
    updatedAt: task.updatedAt,
  }));
}

function saveTasks() {
  try {
    localStorage.setItem(taskStorageKey, JSON.stringify({version: backupVersion, tasks}));
  } catch {
    // The current session still works when browser storage is unavailable.
  }
}

function restoreTasks() {
  try {
    const stored = localStorage.getItem(taskStorageKey);
    if (!stored) return;
    tasks.push(...validateBackup(JSON.parse(stored)));
    nextTaskId = Math.max(0, ...tasks.map((task) => task.id)) + 1;
  } catch (error) {
    storageLoadError = error instanceof Error ? error.message : "저장된 할 일을 불러오지 못했어요.";
  }
}

function announceBackup(message, isError = false) {
  backupStatus.textContent = message;
  backupStatus.classList.toggle("error", isError);
}

function runBackupSelfCheck() {
  const now = new Date().toISOString();
  const task = {
    id: 1,
    title: "백업 검사",
    category: "과제",
    dueDate: "",
    priority: "보통",
    completed: false,
    createdAt: now,
    updatedAt: now,
  };
  console.assert(validateBackup({version: backupVersion, tasks: [task]}).length === 1, "정상 백업을 읽어야 합니다.");
  try {
    validateBackup({version: backupVersion, tasks: [{...task, category: "없는 분류"}]});
    console.error("잘못된 카테고리를 거부해야 합니다.");
  } catch {
    // Expected result.
  }
}

function getDaysUntil(dateString) {
  const [year, month, day] = dateString.split("-").map(Number);
  const today = new Date();
  const dueDay = Date.UTC(year, month - 1, day);
  const currentDay = Date.UTC(today.getFullYear(), today.getMonth(), today.getDate());
  return Math.round((dueDay - currentDay) / dayInMilliseconds);
}

function getDueLabel(task) {
  if (!task.dueDate) return "";

  const daysUntil = getDaysUntil(task.dueDate);
  if (daysUntil < 0) return task.completed ? `마감 ${task.dueDate}` : "기한 지남";
  if (daysUntil === 0) return "오늘";
  return `D-${daysUntil}`;
}

function announce(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function announceFocus(message, isError = false) {
  focusStatus.textContent = message;
  focusStatus.classList.toggle("error", isError);
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const isDark = theme === "dark";
  themeToggle.textContent = isDark ? "라이트 모드" : "다크 모드";
  themeToggle.setAttribute("aria-label", `${isDark ? "라이트" : "다크"} 모드로 전환`);
}

function getVisibleTasks() {
  const query = searchInput.value.trim().toLocaleLowerCase("ko-KR");
  const visibleTasks = tasks.filter((task) => {
    const matchesSearch = !query || task.title.toLocaleLowerCase("ko-KR").includes(query);
    const matchesCategory = categoryFilter.value === "전체" || task.category === categoryFilter.value;
    const matchesStatus = statusFilter.value === "전체"
      || (statusFilter.value === "진행 중" && !task.completed)
      || (statusFilter.value === "완료" && task.completed)
      || (statusFilter.value === "기한 지남" && !task.completed && task.dueDate && getDaysUntil(task.dueDate) < 0);
    return matchesSearch && matchesCategory && matchesStatus;
  });

  return visibleTasks.sort((first, second) => {
    if (sortFilter.value === "deadline") {
      if (!first.dueDate && !second.dueDate) {
        return first.createdAt.localeCompare(second.createdAt) || first.id - second.id;
      }
      if (!first.dueDate) return 1;
      if (!second.dueDate) return -1;
      return first.dueDate.localeCompare(second.dueDate)
        || first.createdAt.localeCompare(second.createdAt)
        || first.id - second.id;
    }
    if (sortFilter.value === "priority") {
      return priorityRanks[second.priority] - priorityRanks[first.priority]
        || first.createdAt.localeCompare(second.createdAt)
        || first.id - second.id;
    }
    return second.createdAt.localeCompare(first.createdAt) || second.id - first.id;
  });
}

function getFocusRecommendation() {
  const incompleteTasks = tasks.filter((task) => !task.completed);
  return incompleteTasks.sort((first, second) => {
    const firstDays = first.dueDate ? getDaysUntil(first.dueDate) : Infinity;
    const secondDays = second.dueDate ? getDaysUntil(second.dueDate) : Infinity;
    const getGroup = (task, days) => {
      if (days < 0) return 0;
      if (days === 0) return 1;
      if (task.priority === "높음") return 2;
      if (Number.isFinite(days)) return 3;
      return 4;
    };
    return getGroup(first, firstDays) - getGroup(second, secondDays)
      || firstDays - secondDays
      || priorityRanks[second.priority] - priorityRanks[first.priority]
      || first.createdAt.localeCompare(second.createdAt);
  })[0] ?? null;
}

function getFocusReason(task) {
  if (!task) return "미완료 할 일을 추가하면 우선순위에 맞춰 추천해 드려요.";
  const days = task.dueDate ? getDaysUntil(task.dueDate) : Infinity;
  if (days < 0) return "기한이 지난 일이라 가장 먼저 추천했어요.";
  if (days === 0) return "오늘 마감인 일이라 먼저 추천했어요.";
  if (task.priority === "높음") return "중요도가 높은 일이라 추천했어요.";
  if (Number.isFinite(days)) return "마감일이 가까운 일이라 추천했어요.";
  return "먼저 등록한 일이라 추천했어요.";
}

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
}

function renderFocus() {
  const activeTask = tasks.find((task) => task.id === focusTaskId) ?? getFocusRecommendation();
  focusTask.textContent = activeTask?.title ?? "추천할 할 일이 아직 없어요.";
  focusReason.textContent = getFocusReason(activeTask);
  focusCountDisplay.textContent = focusCount;
  timerDisplay.value = formatTime(remainingSeconds);
  timerDisplay.textContent = formatTime(remainingSeconds);
  timerStartButton.hidden = timerState !== "idle";
  timerPauseButton.hidden = timerState !== "running";
  timerResumeButton.hidden = timerState !== "paused";
  timerStopButton.hidden = timerState === "idle";
  quickTimeButtons.forEach((button) => {
    button.classList.toggle("selected", Number(button.dataset.minutes) === focusDuration);
  });
}

function readFocusDuration() {
  const minutes = Number(focusDurationInput.value);
  if (!Number.isInteger(minutes) || minutes < 5 || minutes > 120) {
    announceFocus("집중 시간은 5분부터 120분 사이의 정수로 입력해 주세요.", true);
    return null;
  }
  return minutes;
}

function stopTimer(resetDisplay = true) {
  clearInterval(timerInterval);
  timerInterval = null;
  timerState = "idle";
  timerEndTime = 0;
  focusTaskId = null;
  if (resetDisplay) remainingSeconds = focusDuration * 60;
  document.title = "Kiwibird";
  renderFocus();
}

function finishTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
  timerState = "idle";
  timerEndTime = 0;
  remainingSeconds = 0;
  focusTaskId = null;
  focusCount += 1;
  storeSetting(`kiwibird-focus-count-${getLocalDateString()}`, focusCount);
  document.title = "집중 시간이 끝났어요! · Kiwibird";
  announceFocus("집중 시간이 끝났어요! 잠시 쉬어 가세요.");
  renderFocus();
}

function updateTimer() {
  remainingSeconds = Math.max(0, Math.ceil((timerEndTime - Date.now()) / 1000));
  if (remainingSeconds === 0) finishTimer();
  else renderFocus();
}

function setFocusDuration(minutes) {
  if (!Number.isInteger(minutes) || minutes < 5 || minutes > 120) {
    announceFocus("집중 시간은 5분부터 120분 사이의 정수로 입력해 주세요.", true);
    return false;
  }
  if (timerState !== "idle" && !window.confirm("실행 중인 타이머를 초기화하고 시간을 바꿀까요?")) {
    focusDurationInput.value = focusDuration;
    return false;
  }
  if (timerState !== "idle") stopTimer(false);
  focusDuration = minutes;
  remainingSeconds = minutes * 60;
  focusDurationInput.value = minutes;
  storeSetting("kiwibird-focus-duration", minutes);
  announceFocus(`${minutes}분 집중으로 설정했어요.`);
  renderFocus();
  return true;
}

function getNestState(completedCount, totalCount) {
  if (totalCount === 0) {
    return {className: "stage-empty", image: "assets/kiwibird-nest.png", label: "빈 둥지", message: "할 일을 추가하면 둥지에 알이 생겨요."};
  }
  if (completedCount === totalCount) {
    return {className: "stage-complete", image: "assets/kiwibird-nest-bird.png", label: "완성된 둥지와 키위새", message: "오늘 할 일을 모두 끝냈어요!"};
  }
  return {className: "stage-egg", image: "assets/kiwibird-nest-egg.png", label: "알이 있는 둥지", message: "할 일을 모두 마치면 키위새가 태어나요."};
}

function renderDashboard() {
  const completedTasks = tasks.filter((task) => task.completed).length;
  const progress = tasks.length === 0 ? 0 : Math.round((completedTasks / tasks.length) * 100);
  const nestState = getNestState(completedTasks, tasks.length);

  todayCount.textContent = tasks.filter((task) => task.dueDate && getDaysUntil(task.dueDate) === 0).length;
  remainingCount.textContent = tasks.length - completedTasks;
  completedCount.textContent = completedTasks;
  overdueCount.textContent = tasks.filter((task) => !task.completed && task.dueDate && getDaysUntil(task.dueDate) < 0).length;
  overallProgress.value = progress;
  overallProgress.textContent = `${progress}%`;
  progressLabel.textContent = `${progress}%`;
  nestScene.className = `nest-scene ${nestState.className}`;
  nestScene.setAttribute("aria-label", nestState.label);
  if (nestArt.getAttribute("src") !== nestState.image) nestArt.src = nestState.image;
  nestMessage.textContent = nestState.message;

  categoryProgressList.replaceChildren(...categories.map((category) => {
    const categoryTasks = tasks.filter((task) => task.category === category);
    const categoryCompleted = categoryTasks.filter((task) => task.completed).length;
    const categoryProgress = categoryTasks.length === 0
      ? 0
      : Math.round((categoryCompleted / categoryTasks.length) * 100);
    const item = document.createElement("div");
    item.className = `category-progress category-${category}`;

    const name = document.createElement("span");
    name.textContent = category;
    const value = document.createElement("strong");
    value.textContent = `${categoryProgress}%`;
    const bar = document.createElement("progress");
    bar.max = 100;
    bar.value = categoryProgress;
    bar.setAttribute("aria-label", `${category} 완료율 ${categoryProgress}%`);

    item.append(name, value, bar);
    return item;
  }));
}

function cancelEditing(shouldAnnounce = true) {
  if (editingTaskId === null) return;
  editingTaskId = null;
  form.reset();
  formTitle.textContent = "새 할 일";
  submitButton.textContent = "할 일 추가";
  cancelEditButton.hidden = true;
  if (shouldAnnounce) announce("수정을 취소했어요.");
}

function startEditing(task) {
  editingTaskId = task.id;
  input.value = task.title;
  categoryInput.value = task.category;
  dueDateInput.value = task.dueDate;
  priorityInput.value = task.priority;
  formTitle.textContent = `할 일 수정: ${task.title}`;
  submitButton.textContent = "수정 저장";
  cancelEditButton.hidden = false;
  announce("수정할 내용을 확인한 뒤 저장해 주세요.");
  input.focus();
  form.scrollIntoView({behavior: "smooth", block: "center"});
}

function createTaskElement(task) {
  const item = document.createElement("li");
  item.className = `task-item category-${task.category}`;
  item.classList.toggle("completed", task.completed);

  const checkbox = document.createElement("input");
  checkbox.className = "task-checkbox";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute("aria-label", `${task.title} 완료 표시`);
  checkbox.addEventListener("change", () => {
    task.completed = checkbox.checked;
    task.updatedAt = new Date().toISOString();
    renderApp();
    announce(task.completed ? "할 일을 완료했어요." : "할 일을 다시 진행 중으로 바꿨어요.");
  });

  const content = document.createElement("div");
  content.className = "task-content";

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;

  const meta = document.createElement("div");
  meta.className = "task-meta";

  const category = document.createElement("span");
  category.className = "category-badge";
  category.textContent = task.category;

  const priority = document.createElement("span");
  priority.className = `priority-badge priority-${task.priority}`;
  priority.textContent = `중요도 ${task.priority}`;

  meta.append(category, priority);

  const dueLabel = getDueLabel(task);
  if (dueLabel) {
    const due = document.createElement("span");
    due.className = "due-badge";
    due.classList.toggle("overdue", !task.completed && dueLabel === "기한 지남");
    due.textContent = dueLabel;
    meta.append(due);
  }

  content.append(title, meta);
  content.title = "더블 클릭하여 수정";
  content.addEventListener("dblclick", () => startEditing(task));

  const editButton = document.createElement("button");
  editButton.className = "edit-button";
  editButton.type = "button";
  editButton.textContent = "수정";
  editButton.setAttribute("aria-label", `${task.title} 수정`);
  editButton.addEventListener("click", () => startEditing(task));

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete-button";
  deleteButton.type = "button";
  deleteButton.textContent = "삭제";
  deleteButton.setAttribute("aria-label", `${task.title} 삭제`);
  deleteButton.addEventListener("click", () => {
    if (!window.confirm(`“${task.title}”을(를) 삭제할까요?`)) return;
    const taskIndex = tasks.findIndex((itemTask) => itemTask.id === task.id);
    tasks.splice(taskIndex, 1);
    if (editingTaskId === task.id) cancelEditing(false);
    renderApp();
    announce("할 일을 삭제했어요.");
  });

  const actions = document.createElement("div");
  actions.className = "task-actions";
  actions.append(editButton, deleteButton);

  item.append(checkbox, content, actions);
  return item;
}

function renderApp() {
  saveTasks();
  renderDashboard();
  renderFocus();
  renderTasks();
}

function renderTasks() {
  const visibleTasks = getVisibleTasks();

  list.replaceChildren(...visibleTasks.map(createTaskElement));
  emptyState.hidden = visibleTasks.length > 0;
  emptyTitle.textContent = tasks.length === 0
    ? "아직 등록한 할 일이 없어요."
    : "조건에 맞는 할 일이 없어요.";
  emptyDescription.textContent = tasks.length === 0
    ? "오늘 해야 할 일을 하나 적어 보세요."
    : "검색어나 필터 조건을 바꿔 보세요.";
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();

  if (!title) {
    announce("할 일 내용을 입력해 주세요.", true);
    input.focus();
    return;
  }

  const now = new Date().toISOString();
  if (editingTaskId === null) {
    tasks.push({
      id: nextTaskId++,
      title,
      category: categoryInput.value,
      dueDate: dueDateInput.value,
      priority: priorityInput.value,
      completed: false,
      createdAt: now,
      updatedAt: now,
    });
    announce("새 할 일을 추가했어요.");
  } else {
    const task = tasks.find((itemTask) => itemTask.id === editingTaskId);
    Object.assign(task, {
      title,
      category: categoryInput.value,
      dueDate: dueDateInput.value,
      priority: priorityInput.value,
      updatedAt: now,
    });
    editingTaskId = null;
    formTitle.textContent = "새 할 일";
    submitButton.textContent = "할 일 추가";
    cancelEditButton.hidden = true;
    announce("할 일을 수정했어요.");
  }

  form.reset();
  renderApp();
  input.focus();
});

searchInput.addEventListener("input", renderTasks);
statusFilter.addEventListener("change", renderTasks);
categoryFilter.addEventListener("change", renderTasks);
sortFilter.addEventListener("change", renderTasks);
resetFiltersButton.addEventListener("click", () => {
  searchInput.value = "";
  statusFilter.value = "전체";
  categoryFilter.value = "전체";
  sortFilter.value = "recent";
  renderTasks();
  announce("검색과 필터 조건을 초기화했어요.");
});
clearCompletedButton.addEventListener("click", () => {
  const completedTasks = tasks.filter((task) => task.completed);
  if (completedTasks.length === 0) {
    announce("삭제할 완료 항목이 없어요.");
    return;
  }
  if (!window.confirm(`완료한 할 일 ${completedTasks.length}개를 모두 삭제할까요?`)) return;
  if (completedTasks.some((task) => task.id === editingTaskId)) cancelEditing(false);
  for (let index = tasks.length - 1; index >= 0; index -= 1) {
    if (tasks[index].completed) tasks.splice(index, 1);
  }
  renderApp();
  announce("완료한 할 일을 모두 삭제했어요.");
});
cancelEditButton.addEventListener("click", () => cancelEditing());
themeToggle.addEventListener("click", () => {
  const theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(theme);
  storeSetting("kiwibird-theme", theme);
});
quickTimeButtons.forEach((button) => {
  button.addEventListener("click", () => setFocusDuration(Number(button.dataset.minutes)));
});
focusDurationInput.addEventListener("change", () => {
  const minutes = readFocusDuration();
  if (minutes !== null) setFocusDuration(minutes);
});
timerStartButton.addEventListener("click", () => {
  const minutes = readFocusDuration();
  if (minutes === null || !setFocusDuration(minutes)) return;
  const recommendation = getFocusRecommendation();
  if (!recommendation) {
    announceFocus("집중할 미완료 할 일이 없어요.", true);
    return;
  }
  focusTaskId = recommendation.id;
  timerState = "running";
  remainingSeconds = focusDuration * 60;
  timerEndTime = Date.now() + remainingSeconds * 1000;
  document.title = "집중 중 · Kiwibird";
  clearInterval(timerInterval);
  timerInterval = setInterval(updateTimer, 250);
  announceFocus(`${recommendation.title}에 집중을 시작했어요.`);
  renderFocus();
});
timerPauseButton.addEventListener("click", () => {
  updateTimer();
  if (timerState !== "running") return;
  clearInterval(timerInterval);
  timerInterval = null;
  timerState = "paused";
  announceFocus("타이머를 일시정지했어요.");
  renderFocus();
});
timerResumeButton.addEventListener("click", () => {
  timerState = "running";
  timerEndTime = Date.now() + remainingSeconds * 1000;
  timerInterval = setInterval(updateTimer, 250);
  document.title = "집중 중 · Kiwibird";
  announceFocus("집중을 계속할게요.");
  renderFocus();
});
timerStopButton.addEventListener("click", () => {
  if (!window.confirm("집중 타이머를 종료할까요?")) return;
  stopTimer();
  announceFocus("집중 타이머를 종료했어요.");
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") cancelEditing();
  if (event.key === "/" && !["INPUT", "SELECT", "TEXTAREA"].includes(event.target.tagName)) {
    event.preventDefault();
    searchInput.focus();
  }
});

exportButton.addEventListener("click", () => {
  const backup = {
    version: backupVersion,
    exportedAt: new Date().toISOString(),
    tasks,
  };
  const blob = new Blob([JSON.stringify(backup, null, 2)], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `kiwibird-backup-${getLocalDateString()}.json`;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
  announceBackup(`할 일 ${tasks.length}개를 JSON 파일로 내보냈어요.`);
});

importFileInput.addEventListener("change", async () => {
  const [file] = importFileInput.files;
  importFileInput.value = "";
  if (!file) return;

  try {
    const importedTasks = validateBackup(JSON.parse(await file.text()));
    if (!window.confirm(`현재 목록을 가져온 할 일 ${importedTasks.length}개로 바꿀까요?`)) {
      announceBackup("가져오기를 취소했어요.");
      return;
    }
    tasks.splice(0, tasks.length, ...importedTasks);
    nextTaskId = Math.max(0, ...tasks.map((task) => task.id)) + 1;
    cancelEditing(false);
    renderApp();
    announceBackup(`할 일 ${tasks.length}개를 가져왔어요.`);
  } catch (error) {
    announceBackup(error instanceof Error ? error.message : "JSON 파일을 읽지 못했어요.", true);
  }
});

focusDurationInput.value = focusDuration;
focusCount = getStoredFocusCount();
dailyQuote.textContent = dailyQuotes[Math.floor(Math.random() * dailyQuotes.length)];
applyTheme(getStoredTheme());
restoreTasks();
renderDashboard();
renderFocus();
renderTasks();
if (storageLoadError) announceBackup(`저장된 할 일을 불러오지 못했어요: ${storageLoadError}`, true);
if (new URLSearchParams(location.search).has("self-test")) runBackupSelfCheck();
