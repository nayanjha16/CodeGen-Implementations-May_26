const $ = (id) => document.getElementById(id);
const els = {
  repository: $("repository-select"), task: $("task-select"), showcase: $("showcase-select"),
  repositoryDescription: $("repository-description"), showcaseDescription: $("showcase-description"),
  sourcePath: $("source-path"), expected: $("expected-sources"), input: $("input-text"),
  inputLanguage: $("input-language"), runMode: $("run-mode"), runButton: $("run-button"),
  progress: $("run-progress"), healthBanner: $("health-banner"), badges: $("capability-badges"),
  sourcesPanel: $("sources-panel"), sourcesList: $("sources-list"), ragDecision: $("rag-decision"),
  retryInvalid: $("retry-invalid"), comparisonPanel: $("comparison-panel"),
  comparisonSummary: $("comparison-summary"),
};

const arm = (panelSelector, outputId, statusId, languageId) => ({
  panel: document.querySelector(panelSelector), output: $(outputId), status: $(statusId), language: $(languageId),
});
const arms = {
  baselineNoRag: arm('[data-arm="baseline_no_rag"]', "baseline-no-rag-output", "baseline-no-rag-status", "baseline-no-rag-language"),
  baselineRag: arm('[data-arm="baseline_with_rag"]', "baseline-rag-output", "baseline-rag-status", "baseline-rag-language"),
  finetunedNoRag: arm('[data-arm="finetuned_no_rag"]', "finetuned-no-rag-output", "finetuned-no-rag-status", "finetuned-no-rag-language"),
  finetunedRag: arm('[data-arm="finetuned_with_rag"]', "finetuned-rag-output", "finetuned-rag-status", "finetuned-rag-language"),
};

let tasks = [], showcases = [], repositories = [], health = null;
let comparisonResults = { noRag: null, rag: null };
const score = (value) => typeof value === "number" ? value.toFixed(3) : "n/a";

function capability(label, ready, detail = "") {
  const node = document.createElement("span");
  node.className = `capability ${ready ? "ready" : "unavailable"}`;
  node.textContent = `${label}: ${ready ? "ready" : "unavailable"}${detail ? ` · ${detail}` : ""}`;
  return node;
}

function targetForTask(taskId) {
  return tasks.find((row) => row.task_id === taskId)?.target || "Output";
}

function renderOutput(target, normalized, raw) {
  const text = normalized || raw || "";
  const code = target === "Python" || target === "Java";
  target = target || "Output";
  const codeNode = target === "Natural Language" ? target : target.toUpperCase();
  const panel = Object.values(arms).find((item) => item.output === normalized?.element);
  void panel;
  return { text, raw: raw || "", code, codeNode };
}

function validationReason(validation) {
  return validation?.reason || validation?.compiler_stderr || "";
}

function setOutput(
  armState,
  raw,
  validation,
  available = true,
  retried = false,
  firstOutput = null,
  firstValidation = null,
) {
  const target = targetForTask(els.task.value);
  const normalized = validation?.normalized_output || raw || "";
  armState.output.dataset.value = normalized;
  armState.output.classList.toggle("prose", target === "Natural Language");
  const code = armState.output.querySelector("code");
  code.innerHTML = "";
  const lines = (normalized || "").split("\n");
  if (target === "Natural Language") {
    code.textContent = normalized || "(no output)";
  } else {
    for (const [index, line] of lines.entries()) {
      const row = document.createElement("span");
      row.className = "code-line";
      row.dataset.line = String(index + 1);
      row.textContent = line || " ";
      code.appendChild(row);
    }
  }
  const rawNode = armState.panel.querySelector(".raw-output");
  rawNode.textContent = retried
    ? [
        "FIRST ATTEMPT (structurally invalid)",
        firstOutput || "(empty)",
        "",
        "FINAL VALIDATED-RETRY ATTEMPT",
        raw || "(empty)",
      ].join("\n")
    : (raw || "");
  armState.language.textContent = target.toUpperCase();
  armState.status.className = "validation";
  if (!available) {
    armState.status.classList.add("muted"); armState.status.textContent = "Unavailable"; return;
  }
  if (!validation) {
    armState.status.classList.add("muted"); armState.status.textContent = "Not run"; return;
  }
  armState.status.classList.add(validation.valid ? "pass" : "fail");
  armState.status.textContent = retried && validation.valid
    ? "PASS AFTER VALIDATED RETRY"
    : `${validation.status || (validation.valid ? "PASS" : "FAIL")}`;
  const firstReason = validationReason(firstValidation);
  armState.status.title = retried
    ? `Retry used. First attempt: ${firstReason || "structurally invalid"}`
    : validationReason(validation);
}

function refreshShowcases(preferredId = null) {
  const filtered = showcases.filter((row) => row.repository_id === els.repository.value && row.task_id === els.task.value);
  els.showcase.innerHTML = "";
  for (const row of filtered) {
    const option = document.createElement("option"); option.value = row.showcase_id; option.textContent = row.title; els.showcase.appendChild(option);
  }
  if (preferredId && filtered.some((row) => row.showcase_id === preferredId)) els.showcase.value = preferredId;
  applyShowcase(els.showcase.value);
}

function refreshTasks(preferredTask = null) {
  const allowed = new Set(showcases.filter((row) => row.repository_id === els.repository.value).map((row) => row.task_id));
  els.task.innerHTML = "";
  for (const task of tasks.filter((row) => allowed.has(row.task_id))) {
    const option = document.createElement("option"); option.value = task.task_id;
    option.textContent = `${task.task_id}: ${task.source} → ${task.target}`; els.task.appendChild(option);
  }
  if (preferredTask && allowed.has(preferredTask)) els.task.value = preferredTask;
  refreshShowcases();
}

function applyRepository(repositoryId) {
  const repo = repositories.find((row) => row.repository_id === repositoryId);
  if (!repo) return;
  els.repositoryDescription.textContent = `${repo.description}${repo.error ? ` Status: ${repo.error}` : ""}`;
  const ragReady = Boolean(repo.rag_available && repo.loaded);
  for (const option of els.runMode.options) {
    if (option.value === "full" || option.value === "with_rag") option.disabled = !ragReady;
  }
  els.runMode.value = ragReady ? "full" : "no_rag";
  refreshTasks(); updateVisibleArms();
}

function applyShowcase(showcaseId) {
  const row = showcases.find((item) => item.showcase_id === showcaseId);
  if (!row) return;
  els.input.value = row.input_text; els.showcaseDescription.textContent = row.description;
  els.inputLanguage.textContent = `${row.source_language} input → ${row.target_language} output`;
  els.sourcePath.textContent = row.source_path ? `Actual source: ${row.source_path}` : "";
  els.sourcePath.classList.toggle("hidden", !row.source_path);
  els.expected.innerHTML = "";
  if ((row.expected_sources || []).length) {
    const strong = document.createElement("strong"); strong.textContent = "Expected evidence:"; els.expected.appendChild(strong);
    for (const name of row.expected_sources) { const tag = document.createElement("span"); tag.textContent = name; tag.className = "source-tag"; els.expected.appendChild(tag); }
  }
}

async function loadConfiguration() {
  const responses = await Promise.all([fetch("/api/tasks"), fetch("/api/showcases"), fetch("/api/repositories")]);
  if (responses.some((response) => !response.ok)) throw new Error("Could not load UI metadata.");
  [tasks, showcases, repositories] = await Promise.all(responses.map((response) => response.json()));
  els.repository.innerHTML = "";
  for (const repo of repositories) {
    const option = document.createElement("option"); option.value = repo.repository_id;
    option.textContent = `${repo.title}${repo.rag_available && !repo.loaded ? " (index unavailable)" : ""}`; els.repository.appendChild(option);
  }
  els.repository.value = repositories.some((row) => row.repository_id === "ledgerflow") ? "ledgerflow" : repositories[0].repository_id;
  applyRepository(els.repository.value);
}

async function checkHealth() {
  const response = await fetch("/api/health"); if (!response.ok) throw new Error("Health endpoint failed.");
  health = await response.json(); els.badges.innerHTML = "";
  els.badges.append(capability("Baseline", health.baseline_loaded, health.device), capability("Fine-tuned", health.finetuned_loaded), capability("Repository RAG", health.rag_loaded), capability("Corpus RAG", health.rag_corpus_loaded));
  const notes = [];
  if (!health.finetuned_loaded) notes.push(`Fine-tuned adapter: ${health.finetuned_error || "unavailable"}`);
  if (!health.rag_loaded) notes.push(`RAG: ${health.rag_error || "unavailable"}`);
  if (health.rag_mock_embeddings) notes.push("Mock embeddings are active; retrieval results are not valid evidence.");
  els.healthBanner.textContent = notes.join(" "); els.healthBanner.classList.toggle("hidden", !notes.length);
}

function resetArms() {
  Object.values(arms).forEach((item) => setOutput(item, "", null));
  comparisonResults = { noRag: null, rag: null };
  els.comparisonPanel.classList.add("hidden");
  els.comparisonSummary.innerHTML = "";
}

function renderCompare(result, withRag) {
  setOutput(
    withRag ? arms.baselineRag : arms.baselineNoRag,
    result.baseline_output,
    result.baseline_validation,
    true,
    result.baseline_retried,
    result.baseline_first_output,
    result.baseline_first_validation,
  );
  setOutput(
    withRag ? arms.finetunedRag : arms.finetunedNoRag,
    result.finetuned_output || "",
    result.finetuned_validation,
    result.finetuned_available,
    result.finetuned_retried,
    result.finetuned_first_output,
    result.finetuned_first_validation,
  );
  comparisonResults[withRag ? "rag" : "noRag"] = result;
}

function renderRetrieval(result) {
  els.sourcesList.innerHTML = "";
  els.ragDecision.textContent = `${result.rag_decision} · used=${result.rag_used} · top=${score(result.rag_top_score)}`;
  const expected = new Set(showcases.find((row) => row.showcase_id === els.showcase.value)?.expected_sources || []);
  for (const source of result.retrieved_sources || []) {
    const card = document.createElement("article"); card.className = `source-card ${expected.has(source.name) ? "expected-hit" : ""}`;
    const title = document.createElement("strong"); title.textContent = `${source.rank ? `#${source.rank} ` : ""}${source.name}`;
    const path = document.createElement("code"); path.textContent = source.file_path;
    const meta = document.createElement("p"); meta.textContent = `score ${score(source.score)} · dense ${score(source.dense_score)} · lexical ${score(source.lexical_score)} · reranker ${score(source.reranker_score)} · ${source.retrieval_method} · ${source.provenance}`;
    card.append(title, path, meta); els.sourcesList.appendChild(card);
  }
  els.sourcesPanel.classList.remove("hidden");
}

function structuralState(leftValidation, rightValidation) {
  if (!leftValidation || !rightValidation) {
    return { css: "same", text: "Not available for both arms." };
  }
  const left = Boolean(leftValidation.valid);
  const right = Boolean(rightValidation.valid);
  if (!left && right) return { css: "improved", text: "Improved: FAIL → PASS." };
  if (left && !right) return { css: "regressed", text: "Regressed: PASS → FAIL." };
  return {
    css: "same",
    text: left ? "Unchanged: both PASS." : "Unchanged: both FAIL.",
  };
}

function addComparison(title, state) {
  const node = document.createElement("article");
  node.className = `comparison-item ${state.css}`;
  const heading = document.createElement("strong");
  heading.textContent = title;
  const text = document.createElement("span");
  text.textContent = state.text;
  node.append(heading, text);
  els.comparisonSummary.appendChild(node);
}

function renderComparisonSummary() {
  els.comparisonSummary.innerHTML = "";
  const noRag = comparisonResults.noRag;
  const rag = comparisonResults.rag;
  if (noRag) {
    addComparison(
      "Fine-tuning effect · No RAG",
      structuralState(noRag.baseline_validation, noRag.finetuned_validation),
    );
  }
  if (rag) {
    addComparison(
      "Fine-tuning effect · With RAG",
      structuralState(rag.baseline_validation, rag.finetuned_validation),
    );
  }
  if (noRag && rag) {
    addComparison(
      "RAG effect · Fine-tuned",
      structuralState(noRag.finetuned_validation, rag.finetuned_validation),
    );
  }
  els.comparisonPanel.classList.toggle(
    "hidden",
    els.comparisonSummary.children.length === 0,
  );
}

async function compare(useRag) {
  const response = await fetch("/api/compare", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      repository_id: els.repository.value,
      task_id: els.task.value,
      input_text: els.input.value,
      use_rag: useRag,
      retry_invalid: els.retryInvalid.checked,
    }),
  });
  const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || response.statusText); return payload;
}

function updateVisibleArms() {
  const mode = els.runMode.value;
  document.querySelectorAll(".result-panel").forEach((panel) => { const isRag = panel.classList.contains("rag-arm"); panel.classList.toggle("hidden", (mode === "no_rag" && isRag) || (mode === "with_rag" && !isRag)); });
}

async function runTask() {
  if (!els.input.value.trim()) { els.progress.textContent = "Enter input first."; return; }
  resetArms(); els.sourcesPanel.classList.add("hidden"); els.runButton.disabled = true;
  const modes = els.runMode.value === "full" ? [false, true] : [els.runMode.value === "with_rag"];
  try {
    for (let index = 0; index < modes.length; index += 1) {
      const useRag = modes[index]; els.progress.textContent = `Running ${index + 1}/${modes.length}: ${useRag ? "with RAG" : "without RAG"}…`;
      const result = await compare(useRag);
      renderCompare(result, useRag);
      if (useRag) renderRetrieval(result);
      renderComparisonSummary();
    }
    els.progress.textContent = "Completed.";
  } catch (error) { els.progress.textContent = `Failed: ${error.message}`; }
  finally { els.runButton.disabled = false; }
}

els.repository.addEventListener("change", () => applyRepository(els.repository.value));
els.task.addEventListener("change", () => refreshShowcases());
els.showcase.addEventListener("change", () => applyShowcase(els.showcase.value));
els.runMode.addEventListener("change", updateVisibleArms); els.runButton.addEventListener("click", runTask);
document.querySelectorAll(".result-panel").forEach((panel) => {
  const output = panel.querySelector(".code-output");
  panel.querySelector(".copy-output").addEventListener("click", () => navigator.clipboard.writeText(output.dataset.value || ""));
  panel.querySelector(".use-output").addEventListener("click", () => { els.input.value = output.dataset.value || ""; els.input.focus(); });
  panel.querySelector(".download-output").addEventListener("click", () => {
    const target = targetForTask(els.task.value); const extension = target === "Python" ? "py" : target === "Java" ? "java" : "txt";
    const url = URL.createObjectURL(new Blob([output.dataset.value || ""], {type: "text/plain"})); const link = document.createElement("a"); link.href = url; link.download = `repocoder_${els.task.value.toLowerCase()}.${extension}`; link.click(); URL.revokeObjectURL(url);
  });
});

Promise.all([loadConfiguration(), checkHealth()]).catch((error) => { els.healthBanner.textContent = `Initialization failed: ${error.message}`; els.healthBanner.classList.remove("hidden"); });
