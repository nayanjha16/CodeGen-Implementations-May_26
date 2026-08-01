const taskSelect = document.getElementById("task-select");
const inputText = document.getElementById("input-text");
const runButton = document.getElementById("run-button");
const baselineOutput = document.getElementById("baseline-output");
const finetunedOutput = document.getElementById("finetuned-output");
const useBaselineButton = document.getElementById("use-baseline-button");
const useFinetunedButton = document.getElementById("use-finetuned-button");
const healthBanner = document.getElementById("health-banner");

async function loadTasks() {
  const response = await fetch("/api/tasks");
  const tasks = await response.json();
  taskSelect.innerHTML = "";
  for (const task of tasks) {
    const option = document.createElement("option");
    option.value = task.task_id;
    option.textContent = `${task.task_id}: ${task.source} -> ${task.target} -- ${task.description}`;
    taskSelect.appendChild(option);
  }
}

async function checkHealth() {
  const response = await fetch("/api/health");
  const health = await response.json();
  if (!health.finetuned_loaded) {
    healthBanner.textContent =
      "Fine-tuned model is not loaded on this server (no trained adapter found). " +
      "Only baseline output will be available.";
    healthBanner.classList.remove("hidden");
  }
}

async function runTask() {
  runButton.disabled = true;
  runButton.textContent = "Running...";
  baselineOutput.value = "";
  finetunedOutput.value = "";

  try {
    const response = await fetch("/api/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        task_id: taskSelect.value,
        input_text: inputText.value,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      baselineOutput.value = `Error: ${error.detail || response.statusText}`;
      return;
    }

    const result = await response.json();
    baselineOutput.value = result.baseline_output || "";
    finetunedOutput.value = result.finetuned_available
      ? result.finetuned_output || ""
      : "(fine-tuned model not available on this server)";
  } catch (err) {
    baselineOutput.value = `Request failed: ${err}`;
  } finally {
    runButton.disabled = false;
    runButton.textContent = "Run";
  }
}

runButton.addEventListener("click", runTask);
useBaselineButton.addEventListener("click", () => {
  inputText.value = baselineOutput.value;
});
useFinetunedButton.addEventListener("click", () => {
  inputText.value = finetunedOutput.value;
});

loadTasks();
checkHealth();
