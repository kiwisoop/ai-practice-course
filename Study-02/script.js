const tasks = [];
let nextTaskId = 1;

const form = document.querySelector("#task-form");
const input = document.querySelector("#task-input");
const categoryInput = document.querySelector("#category-input");
const dueDateInput = document.querySelector("#due-date-input");
const priorityInput = document.querySelector("#priority-input");
const categoryFilter = document.querySelector("#category-filter");
const list = document.querySelector("#task-list");
const emptyState = document.querySelector("#empty-state");
const emptyTitle = document.querySelector("#empty-title");
const emptyDescription = document.querySelector("#empty-description");
const statusMessage = document.querySelector("#status-message");

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
    renderTasks();
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

  const deleteButton = document.createElement("button");
  deleteButton.className = "delete-button";
  deleteButton.type = "button";
  deleteButton.textContent = "삭제";
  deleteButton.setAttribute("aria-label", `${task.title} 삭제`);
  deleteButton.addEventListener("click", () => {
    if (!window.confirm(`“${task.title}”을(를) 삭제할까요?`)) return;
    const taskIndex = tasks.findIndex((itemTask) => itemTask.id === task.id);
    tasks.splice(taskIndex, 1);
    renderTasks();
    announce("할 일을 삭제했어요.");
  });

  item.append(checkbox, content, deleteButton);
  return item;
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
  input.value = "";
  dueDateInput.value = "";
  renderTasks();
  announce("새 할 일을 추가했어요.");
  input.focus();
});

categoryFilter.addEventListener("change", renderTasks);

renderTasks();
