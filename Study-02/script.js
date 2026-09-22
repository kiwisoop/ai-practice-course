const tasks = [];
let nextTaskId = 1;
let editingTaskId = null;

const categories = ["업무", "과제", "공부", "취미", "개발", "개인"];

const form = document.querySelector("#task-form");
const formTitle = document.querySelector("#task-form-title");
const input = document.querySelector("#task-input");
const categoryInput = document.querySelector("#category-input");
const dueDateInput = document.querySelector("#due-date-input");
const priorityInput = document.querySelector("#priority-input");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit-button");
const categoryFilter = document.querySelector("#category-filter");
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
const nestMessage = document.querySelector("#nest-message");
const categoryProgressList = document.querySelector("#category-progress-list");

const dayInMilliseconds = 86_400_000;

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

function getNestState(progress) {
  if (progress === 100) {
    return {className: "stage-complete", label: "완성된 둥지와 키위새", message: "오늘 할 일을 모두 끝냈어요!"};
  }
  if (progress >= 75) {
    return {className: "stage-bird", label: "키위새가 찾아온 둥지", message: "키위새가 둥지에 찾아왔어요."};
  }
  if (progress >= 50) {
    return {className: "stage-egg", label: "알이 있는 둥지", message: "둥지에 작은 알이 생겼어요."};
  }
  if (progress >= 25) {
    return {className: "stage-leaf", label: "나뭇잎이 생긴 둥지", message: "둥지에 초록 잎이 돋았어요."};
  }
  return {className: "stage-empty", label: "빈 둥지", message: "할 일을 하나씩 완료해 둥지를 채워 보세요."};
}

function renderDashboard() {
  const completedTasks = tasks.filter((task) => task.completed).length;
  const progress = tasks.length === 0 ? 0 : Math.round((completedTasks / tasks.length) * 100);
  const nestState = getNestState(progress);

  todayCount.textContent = tasks.filter((task) => task.dueDate && getDaysUntil(task.dueDate) === 0).length;
  remainingCount.textContent = tasks.length - completedTasks;
  completedCount.textContent = completedTasks;
  overdueCount.textContent = tasks.filter((task) => !task.completed && task.dueDate && getDaysUntil(task.dueDate) < 0).length;
  overallProgress.value = progress;
  overallProgress.textContent = `${progress}%`;
  progressLabel.textContent = `${progress}%`;
  nestScene.className = `nest-scene ${nestState.className}`;
  nestScene.setAttribute("aria-label", nestState.label);
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
  renderDashboard();
  renderTasks();
}

function renderTasks() {
  const visibleTasks = categoryFilter.value === "전체"
    ? tasks
    : tasks.filter((task) => task.category === categoryFilter.value);

  list.replaceChildren(...visibleTasks.map(createTaskElement));
  emptyState.hidden = visibleTasks.length > 0;
  emptyTitle.textContent = tasks.length === 0
    ? "아직 등록한 할 일이 없어요."
    : "이 카테고리에는 할 일이 없어요.";
  emptyDescription.textContent = tasks.length === 0
    ? "오늘 해야 할 일을 하나 적어 보세요."
    : "다른 카테고리를 선택해 보세요.";
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

categoryFilter.addEventListener("change", renderTasks);
cancelEditButton.addEventListener("click", () => cancelEditing());
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") cancelEditing();
});

renderApp();
