// main.js — small client-side enhancements for Afya Kijiji.
// No dependencies, no build step: this is loaded directly via a <script>
// tag before </body> in templates/page.html.

document.addEventListener("DOMContentLoaded", () => {
  initTextSizeControl();
  initHouseSearch();
});

// ---------------------------------------------------------------------
// Text-size control (A / A+ / A++) -- an accessibility affordance for
// older readers or anyone on a small phone screen. Scales the whole page
// via the root font-size (most of the stylesheet is written in rem), and
// remembers the choice in localStorage so it persists across pages.
// ---------------------------------------------------------------------
function initTextSizeControl() {
  const buttons = document.querySelectorAll(".text-size-btn");
  if (!buttons.length) return;

  const applyScale = (scale) => {
    document.documentElement.style.fontSize = scale;
    buttons.forEach((b) => b.classList.toggle("active", b.dataset.scale === scale));
  };

  let saved = null;
  try {
    saved = localStorage.getItem("afyaTextScale");
  } catch (e) {
    /* localStorage unavailable (private mode, etc.) -- fall back to default */
  }
  if (saved) applyScale(saved);

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const scale = btn.dataset.scale;
      applyScale(scale);
      try {
        localStorage.setItem("afyaTextScale", scale);
      } catch (e) {
        /* ignore -- scale still applies for this page view */
      }
    });
  });
}

// ---------------------------------------------------------------------
// Live search on the houses page: filters the .card links inside each
// neighbourhood (and the practical guides grid) by the pre-computed
// data-search string on each card, hiding empty neighbourhood blocks and
// showing a "no results" message when nothing matches.
// ---------------------------------------------------------------------
function initHouseSearch() {
  const input = document.getElementById("house-search");
  if (!input) return;

  const cards = Array.from(document.querySelectorAll("[data-search]"));
  const blocks = Array.from(document.querySelectorAll(".neighbourhood-block"));
  const practicalGrid = document.getElementById("practical-grid");
  const emptyMsg = document.getElementById("search-empty");

  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    let anyVisible = false;

    cards.forEach((card) => {
      const match = !query || card.dataset.search.includes(query);
      card.classList.toggle("search-hidden", !match);
      if (match) anyVisible = true;
    });

    blocks.forEach((block) => {
      const hasVisible = block.querySelectorAll(".card:not(.search-hidden)").length > 0;
      block.classList.toggle("search-hidden", query !== "" && !hasVisible);
    });

    if (practicalGrid) {
      const hasVisible = practicalGrid.querySelectorAll(".card:not(.search-hidden)").length > 0;
      practicalGrid.classList.toggle("search-hidden", query !== "" && !hasVisible);
    }

    if (emptyMsg) emptyMsg.hidden = anyVisible || query === "";
  });
}
