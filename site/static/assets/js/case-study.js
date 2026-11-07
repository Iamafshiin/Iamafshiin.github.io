(() => {
  const prog = document.getElementById("prog");
  if (prog) {
    const update = () => {
      const h = document.documentElement;
      prog.style.width = (h.scrollTop / (h.scrollHeight - h.clientHeight || 1)) * 100 + "%";
    };
    addEventListener("scroll", update, { passive: true });
    update();
  }

  const drop = document.getElementById("drop");
  if (!drop) return;
  const ltv = document.getElementById("ltv");
  const nodes = [0, 1, 2, 3].map((i) => document.getElementById("n" + i));
  const update = () => {
    const d = Number(drop.value);
    const ratio = 55 / (100 * (1 - d / 100));
    const state = ratio < 0.7 ? 0 : ratio < 0.85 ? 1 : ratio < 1 ? 2 : 3;
    nodes.forEach((n, i) => n.classList.toggle("on", i === state));
    ltv.textContent = `-${d}% · LTV ${(ratio * 100).toFixed(0)}%`;
  };
  drop.closest(".ctl").hidden = false;
  drop.addEventListener("input", update);
  update();
})();
