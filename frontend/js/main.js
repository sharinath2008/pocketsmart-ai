// Tab switching
const tabButtons = document.querySelectorAll(".tab-btn");
const planners = document.querySelectorAll(".planner");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    planners.forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// Escape text before putting it in innerHTML so AI/server output can't inject markup.
function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderResult(containerId, data) {
  const container = document.getElementById(containerId);

  if (data.error) {
    container.innerHTML = `<p class="error">${escapeHtml(data.error)}</p>`;
    return;
  }

  const productsHtml = (data.suggested_products || [])
    .map(
      (p) => `
        <div class="product-card">
          <span>${escapeHtml(p.name)}</span>
          <span class="source">${escapeHtml(p.source)} · ₹${escapeHtml(p.estimated_price)}</span>
        </div>`
    )
    .join("");

  container.innerHTML = `
    <div class="recommendation">${escapeHtml(data.recommendation)}</div>
    <div class="products">${productsHtml}</div>
  `;
}

function setLoading(form, isLoading) {
  const btn = form.querySelector("button[type=submit]");
  btn.disabled = isLoading;
  btn.textContent = isLoading ? "Generating..." : "Get Recommendations";
}

// Shared request helper. credentials: "include" lets the session cookie
// travel between GitHub Pages and the backend (needs matching CORS on the server).
async function postToApi(path, options, resultId, form) {
  setLoading(form, true);
  document.getElementById(resultId).innerHTML =
    '<p>Generating... (the first request may take up to a minute if the server was asleep)</p>';
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      credentials: "include",
      ...options,
    });
    const data = await res.json();
    renderResult(resultId, data);
  } catch (err) {
    renderResult(resultId, { error: "Could not reach the server. Please try again." });
  } finally {
    setLoading(form, false);
  }
}

// Home Planner
document.getElementById("home-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  postToApi(
    "/generate-home",
    {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ budget: form.budget.value, details: form.details.value }),
    },
    "home-result",
    form
  );
});

// Party Planner
document.getElementById("party-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  postToApi(
    "/generate-party",
    {
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        budget: form.budget.value,
        event_type: form.event_type.value,
        guests: form.guests.value,
      }),
    },
    "party-result",
    form
  );
});

// Jewelry Planner (multipart, supports image upload)
document.getElementById("jewelry-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const form = e.target;
  postToApi("/generate-jewelry", { body: new FormData(form) }, "jewelry-result", form);
});
