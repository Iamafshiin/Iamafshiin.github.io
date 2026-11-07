(() => {
  const data = JSON.parse(document.getElementById("pal-data").textContent);
  const pal = document.getElementById("pal");
  const input = document.getElementById("palin");
  const list = document.getElementById("pallist");
  const trigger = document.querySelector("[data-pal]");
  const go = (url) => () => (location.href = url);

  const commands = [
    ...data.studies.map((title, i) => [`Read case study: ${title}`, "open", go(`/case-studies/${data.slugs[i]}/`)]),
    ["Download Resume (PDF)", "file", go(data.resume)],
    ["Copy email", "copy", async () => (await window.copyEmail?.(data.email)) || go(`mailto:${data.email}`)()],
    ["Go to Experience", "jump", go("/#experience")],
    ["Open GitHub", "link", go(data.github)],
    ["Open LinkedIn", "link", go(data.linkedin)],
  ];

  let shown = commands;
  let sel = 0;
  let opener = null;

  const draw = () => {
    list.innerHTML = "";
    shown.forEach(([label, kind], i) => {
      const li = document.createElement("li");
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", String(i === sel));
      li.dataset.i = i;
      li.textContent = label;
      const small = document.createElement("small");
      small.textContent = kind;
      li.append(small);
      list.append(li);
    });
  };
  const open = () => {
    opener = document.activeElement;
    pal.hidden = false;
    input.value = "";
    shown = commands;
    sel = 0;
    draw();
    input.focus();
  };
  const close = () => {
    pal.hidden = true;
    opener?.focus();
  };
  const run = (i) => {
    const cmd = shown[i];
    close();
    cmd?.[2]();
  };

  trigger.hidden = false;
  trigger.addEventListener("click", open);
  input.addEventListener("input", () => {
    const q = input.value.toLowerCase();
    shown = commands.filter(([label]) => label.toLowerCase().includes(q));
    sel = 0;
    draw();
  });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown") sel = Math.min(sel + 1, shown.length - 1);
    else if (e.key === "ArrowUp") sel = Math.max(sel - 1, 0);
    else if (e.key === "Enter") return run(sel);
    else if (e.key === "Escape") return close();
    else return;
    e.preventDefault();
    draw();
  });
  list.addEventListener("click", (e) => {
    const li = e.target.closest("li");
    if (li) run(Number(li.dataset.i));
  });
  pal.addEventListener("click", (e) => {
    if (e.target === pal) close();
  });
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      pal.hidden ? open() : close();
      return;
    }
    if (e.target.closest("input, textarea, [contenteditable]")) return;
    if (e.key === "/" && pal.hidden) {
      e.preventDefault();
      open();
    }
  });
})();
