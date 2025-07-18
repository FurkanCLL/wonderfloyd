/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
  let scrollPos = 0;
  const mainNav = document.getElementById('mainNav');
  const headerHeight = mainNav.clientHeight;

  window.addEventListener('scroll', function () {
    const currentTop = document.body.getBoundingClientRect().top * -1;

    if (currentTop < scrollPos) {
      // Scrolling Up
      if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
        mainNav.classList.add('is-visible');
      } else {
        mainNav.classList.remove('is-visible', 'is-fixed');
      }
    } else {
      // Scrolling Down
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

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const categoryId = btn.dataset.category;

      // Görsel olarak aktif butonu değiştir
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Postları çek
      fetch(`/filter-posts/${categoryId}`)
        .then(res => res.text())
        .then(html => {
          postList.innerHTML = html;
        });
    });
  });
});