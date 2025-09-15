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

document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('#category-buttons button');
  const postList = document.getElementById('post-list');
  const loadMoreBtn = document.getElementById('load-more');

  const PAGE_SIZE = 10;
  let currentCategory = 0;   // 0 = All
  let currentOffset = PAGE_SIZE;

  // Kategori seçiminde ilk sayfayı çek
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const categoryId = parseInt(btn.dataset.category, 10);

      // aktif görsel değişim
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      currentCategory = categoryId;
      currentOffset = 0; // reset

      fetch(`/filter-posts/${currentCategory}?offset=${currentOffset}&limit=${PAGE_SIZE}`)
        .then(res => res.json())
        .then(data => {
          postList.innerHTML = data.html;
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
          // ekle (append)
          const tmp = document.createElement('div');
          tmp.innerHTML = data.html;
          // child'ları teker teker taşı
          while (tmp.firstChild) {
            postList.appendChild(tmp.firstChild);
          }

          currentOffset += PAGE_SIZE;

          if (!data.has_more) {
            loadMoreBtn.style.display = 'none';
          }
        });
    });
  }
});
