(() => {
  const motion = matchMedia("(prefers-reduced-motion: no-preference)").matches;
  const fine = matchMedia("(pointer: fine)").matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  window.toast = (text) => {
    const el = $("#toast");
    if (!el) return;
    el.textContent = text;
    el.classList.add("on");
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove("on"), 1600);
  };

  window.copyEmail = async (email) => {
    try {
      await navigator.clipboard.writeText(email);
      toast("✓ email copied to clipboard");
      return true;
    } catch {
      return false;
    }
  };

  document.addEventListener("click", async (e) => {
    const link = e.target.closest("[data-copy]");
    if (!link) return;
    const email = link.textContent.trim();
    if (await copyEmail(email)) e.preventDefault();
  });

  if (motion && fine) {
    document.addEventListener("mousemove", (e) => {
      document.body.style.setProperty("--mx", e.clientX + "px");
      document.body.style.setProperty("--my", e.clientY + "px");
    });
    $$(".card").forEach((card) =>
      card.addEventListener("mousemove", (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty("--x", e.clientX - r.left + "px");
        card.style.setProperty("--y", e.clientY - r.top + "px");
      })
    );
  }

  if (!motion) return;

  const glyphs = "abcdefghijklmnopqrstuvwxyz";
  const heading = $("h1");
  if (heading && $("[data-scr]")) heading.style.minHeight = heading.offsetHeight + "px";
  $$("[data-scr]").forEach((el) => {
    const final = el.textContent;
    let frame = 0;
    const total = 28;
    el.setAttribute("aria-label", final);
    const timer = setInterval(() => {
      el.textContent = [...final]
        .map((ch, i) => (ch === " " || i < (final.length * frame) / total ? ch : glyphs[(Math.random() * glyphs.length) | 0]))
        .join("");
      if (++frame > total) {
        clearInterval(timer);
        el.textContent = final;
        el.removeAttribute("aria-label");
        if (heading) heading.style.minHeight = "";
      }
    }, 32);
  });

  const ledger = $("#ledger");
  if (!ledger) return;
  ledger.classList.add("live");
  const accounts = ledger.dataset.accounts.split(",");
  const sdr = $("#sdr");
  const scr = $("#scr");
  const inv = $("#inv");
  let total = Number(sdr.dataset.v);
  let replays = Number(inv.dataset.r);
  const pick = () => accounts[(Math.random() * accounts.length) | 0];
  const hex = (n) => Math.random().toString(16).slice(2, 2 + n);

  const row = () => {
    const r = Math.random();
    const tx = `<span class="id">tx_${hex(4)}</span> `;
    if (r < 0.14) {
      replays++;
      return `${tx}<span class="rj">REPLAY idem_key=${hex(6)} → 409 rejected</span>`;
    }
    if (r < 0.26) {
      return `${tx}<span class="lk">LOCK ${pick()} acquired · wait ${(Math.random() * 8 + 1).toFixed(1)}ms</span>`;
    }
    const debit = pick();
    let credit = pick();
    if (credit === debit) credit = accounts[(accounts.indexOf(debit) + 1) % accounts.length];
    const amount = (Math.random() * 3.95e6 + 5e4) | 0;
    total += amount;
    return `${tx}<span class="dr">DR</span> <span class="acct">${debit}</span><span class="am">${amount.toLocaleString("en-US")}</span> <span class="cr">CR</span> <span class="acct">${credit}</span><span class="ok">✓</span>`;
  };

  let timer = null;
  const tick = () => {
    const line = document.createElement("div");
    line.innerHTML = row();
    ledger.prepend(line);
    while (ledger.children.length > 12) ledger.lastElementChild.remove();
    sdr.textContent = scr.textContent = total.toLocaleString("en-US");
    inv.textContent = `balanced ✓ · ${replays} replays`;
  };
  const start = () => (timer ??= setInterval(tick, 850));
  const stop = () => {
    clearInterval(timer);
    timer = null;
  };
  new IntersectionObserver(([entry]) => (entry.isIntersecting && !document.hidden ? start() : stop())).observe(ledger);
  document.addEventListener("visibilitychange", () => (document.hidden ? stop() : start()));
})();
