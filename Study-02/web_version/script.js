const tasks = [];
let nextTaskId = 1;

const form = document.querySelector("#task-form");
const input = document.querySelector("#task-input");
const list = document.querySelector("#task-list");
const emptyState = document.querySelector("#empty-state");
const statusMessage = document.querySelector("#status-message");

function announce(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.classList.toggle("error", isError);
}

function createTaskElement(task) {
  const item = document.createElement("li");
  item.className = "task-item";
  item.classList.toggle("completed", task.completed);

  const checkbox = document.createElement("input");
  checkbox.className = "task-checkbox";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute("aria-label", `${task.title} 완료 표시`);
  checkbox.addEventListener("change", () => {
    task.completed = checkbox.checked;
    renderTasks();
    announce(task.completed ? "할 일을 완료했어요." : "할 일을 다시 진행 중으로 바꿨어요.");
  });

  const title = document.createElement("span");
  title.className = "task-title";
  title.textContent = task.title;

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

  item.append(checkbox, title, deleteButton);
  return item;
}

function renderTasks() {
  list.replaceChildren(...tasks.map(createTaskElement));
  emptyState.hidden = tasks.length > 0;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();

  if (!title) {
    announce("할 일 내용을 입력해 주세요.", true);
    input.focus();
    return;
  }

  tasks.push({id: nextTaskId++, title, completed: false});
  input.value = "";
  renderTasks();
  announce("새 할 일을 추가했어요.");
  input.focus();
});

renderTasks();
