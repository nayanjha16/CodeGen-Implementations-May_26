const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const sqlInput = document.getElementById("sql-input");
const sqlPanel = document.getElementById("sql-panel");
const intentSelect = document.getElementById("intent");
const dbSelect = document.getElementById("db-id");
const exampleList = document.getElementById("example-list");
const sendBtn = document.getElementById("send-btn");
const sendSpinner = document.getElementById("send-spinner");
const btnLabel = document.querySelector("#send-btn .btn-label");
const statusBar = document.getElementById("status-bar");
const statusText = document.getElementById("status-text");
const clearBtn = document.getElementById("clear-btn");

const SQL_INTENTS = new Set(["sql2nosql", "explain_sql", "validate_sql"]);
const QUERY_TIMEOUT_MS = 180000;

const PROGRESS_STEPS = [
  "Extracting schema from the database…",
  "Calling CodeGen API to generate SQL…",
  "Running the query against Postgres…",
  "Summarizing results with Ollama…",
];

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function toggleSqlPanel() {
  const intent = intentSelect.value;
  const show = SQL_INTENTS.has(intent);
  sqlPanel.classList.toggle("hidden", !show);
}

function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  sendSpinner.classList.toggle("hidden", !isLoading);
  btnLabel.classList.toggle("hidden", isLoading);
}

function appendMessage(role, html, extraClass = "") {
  const article = document.createElement("article");
  article.className = `message ${role} ${extraClass}`.trim();
  article.innerHTML = `
    <div class="avatar">${role === "user" ? "You" : "AI"}</div>
    <div class="bubble">${html}</div>
  `;
  messagesEl.appendChild(article);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return article;
}

function createTypingIndicator() {
  const article = appendMessage(
    "assistant",
    `
      <p class="typing-label">Working on your question<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span></p>
      <p class="muted typing-step">Starting agent pipeline…</p>
      <p class="muted typing-elapsed">Elapsed: 0s · typical wait 30–90s</p>
    `,
    "typing"
  );

  const stepEl = article.querySelector(".typing-step");
  const elapsedEl = article.querySelector(".typing-elapsed");
  const started = Date.now();
  let stepIndex = 0;

  const timer = window.setInterval(() => {
    const seconds = Math.floor((Date.now() - started) / 1000);
    elapsedEl.textContent = `Elapsed: ${seconds}s · typical wait 30–90s`;

    const nextStep = Math.min(
      PROGRESS_STEPS.length - 1,
      Math.floor(seconds / 12)
    );
    if (nextStep !== stepIndex) {
      stepIndex = nextStep;
      stepEl.textContent = PROGRESS_STEPS[stepIndex];
    }
  }, 1000);

  return {
    element: article,
    stop() {
      window.clearInterval(timer);
      article.remove();
    },
  };
}

function renderCodeBlock(label, code) {
  if (!code || !String(code).trim()) return "";
  return `
    <div class="code-block">
      <header>${escapeHtml(label)}</header>
      <pre>${escapeHtml(String(code).trim())}</pre>
    </div>
  `;
}

function normalizeRows(rows) {
  if (Array.isArray(rows)) return rows;
  return [];
}

function renderRows(rows) {
  const normalized = normalizeRows(rows);
  if (normalized.length === 0) return "";
  const columns = Object.keys(normalized[0] || {});
  if (columns.length === 0) return "";
  const head = columns.map((col) => `<th>${escapeHtml(col)}</th>`).join("");
  const body = normalized
    .slice(0, 20)
    .map((row) => {
      const cells = columns
        .map((col) => `<td>${escapeHtml(row[col] ?? "")}</td>`)
        .join("");
      return `<tr>${cells}</tr>`;
    })
    .join("");
  const note =
    normalized.length > 20
      ? `<p class="muted">Showing first 20 of ${normalized.length} rows.</p>`
      : "";
  return `
    ${note}
    <div class="results-table-wrap">
      <table class="results-table">
        <thead><tr>${head}</tr></thead>
        <tbody>${body}</tbody>
      </table>
    </div>
  `;
}

function renderAssistantResponse(data) {
  const parts = [];
  parts.push(`<div class="meta">Intent: ${escapeHtml(data.intent || "unknown")}</div>`);
  if (data.error) {
    parts.push(`<p class="error-text">${escapeHtml(data.error)}</p>`);
  }
  if (data.answer) {
    parts.push(`<p>${escapeHtml(data.answer).replaceAll("\n", "<br>")}</p>`);
  }
  parts.push(renderCodeBlock("SQL", data.sql));
  parts.push(renderCodeBlock("MongoDB", data.mongo_query));
  parts.push(renderCodeBlock("Documentation", data.documentation));
  parts.push(renderRows(data.rows));
  return parts.filter(Boolean).join("");
}

async function parseErrorResponse(res) {
  try {
    const data = await res.json();
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((d) => d.msg || String(d)).join("; ");
    return "Request failed";
  } catch (_err) {
    return `Request failed (${res.status})`;
  }
}

async function fetchWithTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    window.clearTimeout(timer);
  }
}

async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    if (!res.ok) throw new Error("Health check failed");
    const data = await res.json();
    statusBar.classList.add("ok");
    statusText.textContent = `${data.demo_db_id} · ${data.orchestrator_model}`;
    if (window.AGENT_UI?.defaultDbId) {
      dbSelect.value = window.AGENT_UI.defaultDbId;
    }
  } catch (_err) {
    statusBar.classList.add("error");
    statusText.textContent = "Agent API unavailable";
  }
}

async function loadExamples() {
  const res = await fetch("/api/examples");
  const examples = await res.json();
  window.__agentExamples = examples;
  exampleList.innerHTML = examples
    .map(
      (item, index) => `
      <button type="button" class="example-btn" data-index="${index}">
        <strong>${escapeHtml(item.label)}</strong>
        <span>${escapeHtml(item.id)} · ${escapeHtml(item.intent)}</span>
      </button>
    `
    )
    .join("");

  exampleList.querySelectorAll(".example-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const item = window.__agentExamples[Number(btn.dataset.index)];
      messageInput.value = item.message || "";
      intentSelect.value = item.intent || "auto";
      sqlInput.value = item.sql || "";
      toggleSqlPanel();
      messageInput.focus();
    });
  });
}

async function submitQuery(event) {
  event.preventDefault();
  const message = messageInput.value.trim();
  const sql = sqlInput.value.trim();
  if (!message && !sql) return;

  appendMessage("user", `<p>${escapeHtml(message || sql)}</p>`);
  messageInput.value = "";

  const typing = createTypingIndicator();
  setLoading(true);

  try {
    const payload = {
      message: message || sql,
      intent: intentSelect.value,
      sql: sql || null,
      db_id: dbSelect.value,
    };

    const res = await fetchWithTimeout(
      "/api/query",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      QUERY_TIMEOUT_MS
    );

    const data = await res.json();
    typing.stop();

    if (!res.ok) {
      let detail = "Request failed";
      if (typeof data.detail === "string") detail = data.detail;
      else if (Array.isArray(data.detail)) {
        detail = data.detail.map((item) => item.msg || String(item)).join("; ");
      }
      appendMessage("assistant", `<p class="error-text">${escapeHtml(detail)}</p>`);
      return;
    }

    appendMessage("assistant", renderAssistantResponse(data));
  } catch (err) {
    typing.stop();
    const messageText =
      err.name === "AbortError"
        ? "Request timed out after 3 minutes. Check CodeGen API, Ollama, and Postgres, then try again."
        : err.message || "Network error";
    appendMessage("assistant", `<p class="error-text">${escapeHtml(messageText)}</p>`);
  } finally {
    setLoading(false);
  }
}

function clearChat() {
  messagesEl.innerHTML = `
    <article class="message assistant welcome">
      <div class="avatar">AI</div>
      <div class="bubble">
        <p>Chat cleared. Ask another database question.</p>
        <p class="muted">Responses usually take 30–90 seconds (schema → CodeGen → execute → summarize).</p>
      </div>
    </article>
  `;
}

intentSelect.addEventListener("change", toggleSqlPanel);
formEl.addEventListener("submit", submitQuery);
clearBtn.addEventListener("click", clearChat);

messageInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

toggleSqlPanel();
loadHealth();
loadExamples();
