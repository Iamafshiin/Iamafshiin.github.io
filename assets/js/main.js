/* Afshin Hasani — portfolio enhancements
   Small, dependency-free. Everything here is progressive:
   the page works fully without this file. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Footer year ---------- */
  var yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  /* ---------- Header shadow on scroll ---------- */
  var head = document.getElementById('site-head');
  var ticking = false;

  function onScroll() {
    if (!head) return;
    head.classList.toggle('is-scrolled', window.scrollY > 8);
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });
  onScroll();

  /* ---------- Mobile navigation ---------- */
  var toggle = document.getElementById('nav-toggle');
  var nav = document.getElementById('nav');

  function setNav(open) {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('is-open', open);
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      setNav(toggle.getAttribute('aria-expanded') !== 'true');
    });

    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) setNav(false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        setNav(false);
        toggle.focus();
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 879) setNav(false);
    });
  }

  /* ---------- Scroll reveal ---------- */
  var revealItems = document.querySelectorAll('.reveal');

  function showAll() {
    revealItems.forEach(function (el) { el.classList.add('is-in'); });
  }

  if ('IntersectionObserver' in window && !reduceMotion) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        revealObserver.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    revealItems.forEach(function (el) { revealObserver.observe(el); });

    /* Safety net: never leave content invisible if the observer misbehaves. */
    window.setTimeout(showAll, 2500);
  } else {
    showAll();
  }

  /* ---------- Active section in nav ---------- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav a[href^="#"]'));
  var sections = navLinks
    .map(function (link) { return document.querySelector(link.getAttribute('href')); })
    .filter(Boolean);

  if ('IntersectionObserver' in window && sections.length) {
    var visible = new Set();

    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) visible.add(entry.target.id);
        else visible.delete(entry.target.id);
      });

      var current = null;
      navLinks.forEach(function (link) {
        var id = link.getAttribute('href').slice(1);
        if (visible.has(id)) current = current || id;
      });

      navLinks.forEach(function (link) {
        var id = link.getAttribute('href').slice(1);
        if (id === current) link.setAttribute('aria-current', 'true');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-45% 0px -45% 0px' });

    sections.forEach(function (section) { sectionObserver.observe(section); });
  }

  /* ---------- Copy email ---------- */
  var copyButton = document.getElementById('copy-email');

  if (copyButton) {
    var label = copyButton.textContent;
    var resetTimer;

    copyButton.addEventListener('click', function () {
      var value = copyButton.getAttribute('data-copy') || '';
      var done = function (ok) {
        copyButton.textContent = ok ? 'Copied' : 'Press Ctrl+C';
        window.clearTimeout(resetTimer);
        resetTimer = window.setTimeout(function () {
          copyButton.textContent = label;
        }, 1800);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(
          function () { done(true); },
          function () { done(false); }
        );
      } else {
        done(false);
      }
    });
  }
})();
