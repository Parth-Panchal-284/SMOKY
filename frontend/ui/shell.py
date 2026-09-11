"""Assemble the Operating Room HTML document."""

from __future__ import annotations

from models.run_state import RunState
from ui.event_feed import render_event_feed
from ui.header import render_header
from ui.operation_header import render_operation_header
from ui.patient_vitals import render_patient_vitals
from ui.rocketride_pipeline import render_pipeline
from ui.sidebar import render_sidebar
from ui.specialist_card import render_specialist_card
from ui.styles import APP_CSS

FONT_LINKS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
"""

FILTER_JS = """
<script>
(function () {
  const filters = document.querySelectorAll("[data-filter]");
  const rows = document.querySelectorAll(".feed-row");
  filters.forEach((btn) => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-filter");
      filters.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      rows.forEach((row) => {
        const cat = row.getAttribute("data-cat") || "system";
        row.style.display = (key === "all" || cat === key) ? "" : "none";
      });
    });
  });

  function tickClock() {
    const now = new Date();
    const dateEl = document.getElementById("clock-date");
    const timeEl = document.getElementById("clock-time");
    if (!dateEl || !timeEl) return;
    const date = now.toLocaleDateString("en-US", {
      weekday: "short", month: "short", day: "numeric", year: "numeric"
    });
    dateEl.textContent = date;
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12;
    timeEl.textContent = hours + ":" + minutes + " " + ampm;
  }
  tickClock();
  setInterval(tickClock, 1000);
})();
</script>
"""


def render_app_html(state: RunState, current: str = "operating") -> str:
    cards = "".join(render_specialist_card(a) for a in state.agents())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1280, initial-scale=1">
  {FONT_LINKS}
  <style>{APP_CSS}</style>
</head>
<body>
  <div class="app">
    {render_header(state)}
    {render_sidebar(current)}
    <main class="main">
      <div class="main-grid">
        {render_operation_header(state)}
        {cards}
        {render_patient_vitals(state)}
        {render_event_feed(state)}
        {render_pipeline(state)}
      </div>
    </main>
  </div>
  {FILTER_JS}
</body>
</html>
"""


def render_app_fragment(state: RunState, current: str = "operating") -> str:
    """The same console, WITHOUT the document wrapper.

    st.iframe sandboxes its frame: links cannot escape it (so the sidebar could
    not navigate) and the host page needs chrome-hiding CSS that also flattens
    every native Streamlit widget. Rendering the markup inline instead makes the
    sidebar plain same-page anchors and leaves Streamlit's own widgets usable.
    """
    cards = "".join(render_specialist_card(a) for a in state.agents())
    return f"""
{FONT_LINKS}
<style>{APP_CSS}</style>
<div class="app">
  {render_header(state)}
  {render_sidebar(current)}
  <main class="main">
    <div class="main-grid">
      {render_operation_header(state)}
      {cards}
      {render_patient_vitals(state)}
      {render_event_feed(state)}
      {render_pipeline(state)}
    </div>
  </main>
</div>
"""
