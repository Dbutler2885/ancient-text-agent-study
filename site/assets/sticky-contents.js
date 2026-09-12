// Pins the contents to the top once the opening scrolls away.
// Its height sizes the opening to one viewport and offsets in-page anchor targets.
(() => {
  const contents = document.getElementById('article-contents');
  if (!contents) return;
  const root = document.documentElement;
  new ResizeObserver(() => root.style.setProperty('--article-contents-height', contents.offsetHeight + 'px')).observe(contents);
  const sentinel = document.createElement('div');
  sentinel.setAttribute('aria-hidden', 'true');
  contents.before(sentinel);
  new IntersectionObserver(([entry]) => contents.classList.toggle('is-stuck', !entry.isIntersecting && entry.boundingClientRect.top < 0)).observe(sentinel);
})();
