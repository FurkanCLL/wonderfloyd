// ====================== NAVBAR SCROLL BEHAVIOR ======================
window.addEventListener('DOMContentLoaded', () => {
  let scrollPos = 0;
  const mainNav = document.getElementById('mainNav');
  const headerHeight = mainNav.clientHeight;

  window.addEventListener('scroll', function () {
    const currentTop = document.body.getBoundingClientRect().top * -1;

    if (currentTop < scrollPos) {
      if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
        mainNav.classList.add('is-visible');
      } else {
        mainNav.classList.remove('is-visible', 'is-fixed');
      }
    } else {
      mainNav.classList.remove('is-visible');
      if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
        mainNav.classList.add('is-fixed');
      }
    }
    scrollPos = currentTop;
  });
});

// ====================== CATEGORY FILTER + LOAD MORE ======================
document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('#category-buttons button');
  const postList = document.getElementById('post-list');
  const loadMoreBtn = document.getElementById('load-more');

  const PAGE_SIZE = 10;
  let currentCategory = 0;   // 0 = All
  let currentOffset = PAGE_SIZE;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const categoryId = parseInt(btn.dataset.category, 10);

      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      currentCategory = categoryId;
      currentOffset = 0; // reset

      fetch(`/filter-posts/${currentCategory}?offset=${currentOffset}&limit=${PAGE_SIZE}`)
        .then(res => res.json())
        .then(data => {
          postList.innerHTML = data.html;

          wfRevealPosts(postList.querySelectorAll('article, .wf-empty'));
          window._wfObservePosts(postList.querySelectorAll('article, .wf-empty'));

          currentOffset += PAGE_SIZE;
          if (data.has_more) {
            loadMoreBtn.style.display = 'inline-block';
          } else {
            loadMoreBtn.style.display = 'none';
          }
        });
    });
  });

  // Load more
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      fetch(`/filter-posts/${currentCategory}?offset=${currentOffset}&limit=${PAGE_SIZE}`)
        .then(res => res.json())
        .then(data => {

          const tmp = document.createElement('div');
          tmp.innerHTML = data.html;

          const newNodes = [];
          while (tmp.firstChild) {
            const n = tmp.firstChild;
            newNodes.push(n);
            postList.appendChild(n);
          }
          wfRevealPosts(newNodes);
          window._wfObservePosts(newNodes);

          currentOffset += PAGE_SIZE;

          if (!data.has_more) {
            loadMoreBtn.style.display = 'none';
          }
        });
    });
  }
});

// ====================== BACK TO TOP ======================
(function () {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  const SHOW_OFFSET = 600;
  let lastY = window.scrollY;

  function onScroll() {
    const y = window.scrollY;

    if (y < SHOW_OFFSET) {
      btn.classList.remove('show');
    } else {
      if (y < lastY) {
        btn.classList.add('show');
      } else {
        btn.classList.remove('show');
      }
    }
    lastY = y;
  }

  btn.addEventListener('click', () => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
  });

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
})();

// ====================== WF POST REVEAL (MASTHEAD-LIKE, SOFTER) ======================
// Soft, yumuşak blur + fade + çok hafif gecikme (stagger). Daha “patlamasın” diye easing yumuşak.
function wfRevealPosts(nodeList) {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const nodes = Array.from(nodeList || []);
  nodes.forEach((el, i) => {
    el.classList.remove('wf-reveal'); // reset
    void el.offsetWidth;              // reflow to restart reliably
    const delay = reduce ? 0 : i * 60;
    setTimeout(() => el.classList.add('wf-reveal'), delay);
  });
}

// İlk yüklemede uygula
document.addEventListener('DOMContentLoaded', () => {
  const initial = document.querySelectorAll('#post-list article, #post-list .wf-empty');
  wfRevealPosts(initial);
});

// ===== WF Post Reveal — scroll triggered with IntersectionObserver =====
(function () {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Create a single observer reused for all posts
  const io = !reduce && 'IntersectionObserver' in window
    ? new IntersectionObserver((entries, obs) => {
        entries.forEach((entry, idx) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            // gentle stagger within the same batch
            setTimeout(() => {
              el.classList.add('wf-reveal');
              el.classList.remove('wf-observe');
            }, idx * 60);
            obs.unobserve(el);
          }
        });
      }, {
        root: null,
        rootMargin: '0px 0px -10% 0px',
        threshold: 0.12
      })
    : null;

  function wfObservePosts(nodeList) {
    const nodes = Array.from(nodeList || []);
    nodes.forEach(el => {
      // reset state
      el.classList.remove('wf-reveal');
      el.classList.add('wf-observe');
      if (io) {
        io.observe(el);
      } else {
        // Fallback
        el.classList.add('wf-reveal');
        el.classList.remove('wf-observe');
      }
    });
  }

  // Initial attach on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    const initial = document.querySelectorAll('#post-list article, #post-list .wf-empty');
    wfObservePosts(initial);
  });

  // Expose for fetch handlers
  window._wfObservePosts = wfObservePosts;
})();


// ===== WonderFloyd Theme Toggle (switch UI + persist) =====
(function () {
  const btn = document.getElementById('wfThemeToggle');
  if (!btn) return;
  const root = document.documentElement;

  function applyTheme(mode) {
    // set attributes
    root.setAttribute('data-theme', mode);
    if (mode === 'dark') root.setAttribute('data-bs-theme', 'dark');
    else root.removeAttribute('data-bs-theme');
    localStorage.setItem('wf-theme', mode);

    // switch UI
    btn.classList.toggle('is-dark', mode === 'dark');
    btn.classList.toggle('is-light', mode === 'light');
    btn.setAttribute('aria-checked', mode === 'dark' ? 'true' : 'false');
  }

  // initial from storage (default dark)
  applyTheme(localStorage.getItem('wf-theme') || 'dark');

  btn.addEventListener('click', () => {
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  // resync on bfcache/back
  window.addEventListener('pageshow', () => {
    applyTheme(localStorage.getItem('wf-theme') || 'dark');
  });
})();



// ===== WonderFloyd Theme Resync (back/forward navigation) =====
(function () {
  function syncThemeFromStorage(updateButtonUI = false) {
    var root = document.documentElement;
    var saved = localStorage.getItem('wf-theme') || 'dark';
    var current = root.getAttribute('data-theme');

    if (current !== saved) {
      root.setAttribute('data-theme', saved);
      if (saved === 'dark') {
        root.setAttribute('data-bs-theme', 'dark');
      } else {
        root.removeAttribute('data-bs-theme');
      }
    }

    // update toggle button label/icon if present (optional)
    if (updateButtonUI) {
      var btn = document.getElementById('wfThemeToggle');
      if (btn) {
        var icon = btn.querySelector('.wf-theme-icon');
        var text = btn.querySelector('.wf-theme-text');
        if (saved === 'dark') {
          if (icon) icon.textContent = '🌙';
          if (text) text.textContent = 'Dark';
          btn.setAttribute('aria-pressed', 'true');
        } else {
          if (icon) icon.textContent = '☀️';
          if (text) text.textContent = 'Light';
          btn.setAttribute('aria-pressed', 'false');
        }
      }
    }
  }

  window.addEventListener('pageshow', function (evt) {
    // if evt.persisted: true then bfcache;
    syncThemeFromStorage(true);
  });

  window.addEventListener('popstate', function () {
    syncThemeFromStorage(true);
  });
})();
