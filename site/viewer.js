/* The page viewer of the home pages (site/index.html, site/he/index.html).
   Each page sets window.SF_VIEWER = { start, t: {page, of}, rtl, docs: {key: {name,
   label, dir, prefix, pdf, ltr, pages: [[title, description], ...]}} } before loading
   this file. Page images: <dir><prefix>-NN.webp, thumbnails <dir><prefix>-NN-t.webp
   (scripts/site-samples.py). A doc with ltr: true is a left-to-right page (the
   lightbox opens at its left edge; Hebrew pages open at the right). */
(function () {
  var C = window.SF_VIEWER;
  if (!C) return;
  var DOCS = C.docs, T = C.t, RTL = !!C.rtl;
  var file = function (kind, n, thumb) {
    var d = DOCS[kind];
    return d.dir + d.prefix + '-' + (n < 10 ? '0' : '') + n + (thumb ? '-t' : '') + '.webp';
  };

  var viewer = document.getElementById('viewer');
  var img = document.getElementById('page-img');
  var sheet = viewer.querySelector('.sheet');
  var countEl = document.getElementById('page-count');
  var titleEl = document.getElementById('page-title');
  var descEl = document.getElementById('page-desc');
  var pdfLink = document.getElementById('pdf-link');
  var thumbs = document.getElementById('thumbs');
  var tabs = viewer.querySelectorAll('[role=tab]');
  var lb = document.getElementById('lightbox');
  var lbImg = document.getElementById('lb-img');
  var lbCount = document.getElementById('lb-count');
  var kind = C.start, page = 1;

  function total() { return DOCS[kind].pages.length; }

  function buildThumbs() {
    thumbs.innerHTML = '';
    DOCS[kind].pages.forEach(function (p, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', T.page + ' ' + (i + 1) + ': ' + p[0]);
      b.innerHTML = '<img src="' + file(kind, i + 1, true) + '" alt="" loading="lazy" width="220" height="311"><span>' + (i + 1) + '</span>';
      b.addEventListener('click', function () { show(i + 1); });
      thumbs.appendChild(b);
    });
  }

  function show(n) {
    page = Math.max(1, Math.min(total(), n));
    var d = DOCS[kind], p = d.pages[page - 1];
    var src = file(kind, page);
    img.src = src;
    img.alt = T.page + ' ' + page + ' ' + T.of + ' ' + d.name + ': ' + p[0];
    sheet.href = src;
    countEl.textContent = T.page + ' ' + page + ' ' + T.of + ' ' + total();
    titleEl.textContent = p[0];
    descEl.textContent = p[1];
    pdfLink.style.display = d.pdf ? '' : 'none';
    if (d.pdf) pdfLink.href = d.pdf;
    viewer.querySelector('.prev').disabled = page === 1;
    viewer.querySelector('.next').disabled = page === total();
    Array.prototype.forEach.call(thumbs.children, function (t, i) {
      t.classList.toggle('active', i === page - 1);
      if (i === page - 1) t.setAttribute('aria-current', 'page'); else t.removeAttribute('aria-current');
    });
    var active = thumbs.children[page - 1];
    if (active) {
      var r = active.getBoundingClientRect(), c = thumbs.getBoundingClientRect();
      thumbs.scrollBy({ left: (r.left + r.width / 2) - (c.left + c.width / 2), behavior: 'smooth' });
    }
    if (page < total()) { var pre = new Image(); pre.src = file(kind, page + 1); }
    if (!lb.hidden) syncLightbox();
  }

  function switchDoc(k) {
    kind = k;
    Array.prototype.forEach.call(tabs, function (t) { t.setAttribute('aria-selected', String(t.dataset.doc === k)); });
    buildThumbs();
    show(1);
  }

  function syncLightbox() {
    lbImg.src = file(kind, page);
    lbImg.alt = img.alt;
    lbCount.textContent = DOCS[kind].label + ' · ' + T.page + ' ' + page + ' ' + T.of + ' ' + total();
    var sc = lb.querySelector('.lb-scroll');
    sc.scrollTop = 0;
    // Hebrew lines start at the right; in an RTL document scrollLeft runs from 0 leftwards
    if (DOCS[kind].ltr) sc.scrollLeft = RTL ? -sc.scrollWidth : 0;
    else sc.scrollLeft = RTL ? 0 : sc.scrollWidth;
  }
  function openLightbox() {
    lb.hidden = false; document.body.classList.add('locked');
    syncLightbox();
    document.getElementById('lb-close').focus();
  }
  function closeLightbox() { lb.hidden = true; document.body.classList.remove('locked'); viewer.focus({ preventScroll: true }); }

  // In a right-to-left page the "next" arrow points left.
  var fwd = RTL ? 'ArrowLeft' : 'ArrowRight', back = RTL ? 'ArrowRight' : 'ArrowLeft';

  Array.prototype.forEach.call(tabs, function (t) { t.addEventListener('click', function () { switchDoc(t.dataset.doc); }); });
  viewer.querySelector('.prev').addEventListener('click', function () { show(page - 1); });
  viewer.querySelector('.next').addEventListener('click', function () { show(page + 1); });
  sheet.addEventListener('click', function (e) { e.preventDefault(); openLightbox(); });
  document.getElementById('zoom').addEventListener('click', openLightbox);
  document.getElementById('lb-prev').addEventListener('click', function () { show(page - 1); });
  document.getElementById('lb-next').addEventListener('click', function () { show(page + 1); });
  document.getElementById('lb-close').addEventListener('click', closeLightbox);
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb-scroll')) closeLightbox(); });

  viewer.addEventListener('keydown', function (e) {
    if (e.key === back) { show(page - 1); e.preventDefault(); }
    if (e.key === fwd) { show(page + 1); e.preventDefault(); }
  });
  document.addEventListener('keydown', function (e) {
    if (lb.hidden) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === back) show(page - 1);
    if (e.key === fwd) show(page + 1);
  });

  var x0 = null;
  sheet.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  sheet.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) { show(page + ((dx < 0) !== RTL ? 1 : -1)); }
  });

  switchDoc(kind);
})();
