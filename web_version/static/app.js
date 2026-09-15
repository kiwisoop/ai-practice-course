// Created with Codex on 2026-09-10.
const canvas = document.querySelector("#drawing");
const context = canvas.getContext("2d");
const result = document.querySelector("#result");
let drawing = false;

function resetCanvas() {
  context.fillStyle = "black";
  context.fillRect(0, 0, canvas.width, canvas.height);
  result.textContent = "Result: -";
}

function point(event) {
  const bounds = canvas.getBoundingClientRect();
  const source = event.touches ? event.touches[0] : event;
  return {
    x: (source.clientX - bounds.left) * canvas.width / bounds.width,
    y: (source.clientY - bounds.top) * canvas.height / bounds.height,
  };
}

function startDrawing(event) {
  drawing = true;
  const position = point(event);
  context.beginPath();
  context.moveTo(position.x, position.y);
  event.preventDefault();
}

function draw(event) {
  if (!drawing) return;
  const position = point(event);
  context.strokeStyle = "white";
  context.lineWidth = 18;
  context.lineCap = "round";
  context.lineJoin = "round";
  context.lineTo(position.x, position.y);
  context.stroke();
  event.preventDefault();
}

function stopDrawing() {
  drawing = false;
  context.closePath();
}

canvas.addEventListener("pointerdown", startDrawing);
canvas.addEventListener("pointermove", draw);
window.addEventListener("pointerup", stopDrawing);

document.querySelector("#clear").addEventListener("click", resetCanvas);
document.querySelector("#recognize").addEventListener("click", async () => {
  result.textContent = "Recognizing...";
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({image: canvas.toDataURL("image/png")}),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Recognition failed.");
    result.textContent = `Result: ${data.digit}   Confidence: ${(data.confidence * 100).toFixed(1)}%`;
  } catch (error) {
    result.textContent = error.message;
  }
});

resetCanvas();
