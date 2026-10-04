// Enhance complete static HTML without replacing images or Pin links.
(() => {
  const grid = document.getElementById('ideaGrid');
  if (!grid) return;
  const cards = [...grid.querySelectorAll('.ideaCardWrap')];
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const input = document.getElementById('searchInput');
  const status = document.getElementById('searchStatus');
  const empty = document.getElementById('emptyState');
  let category = 'all';
  function filter() {
    const query = (input?.value || '').trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const text = `${card.dataset.title} ${card.dataset.cat}`.toLocaleLowerCase();
      card.hidden = (category !== 'all' && card.dataset.cat !== category) || !text.includes(query);
      if (!card.hidden) count++;
    }
    if (empty) empty.hidden = count > 0;
    if (status) status.textContent = `${count} guide${count === 1 ? '' : 's'} found`;
  }
  for (const button of buttons) button.addEventListener('click', () => {
    category = button.dataset.filter;
    for (const item of buttons) {
      item.classList.toggle('active', item === button);
      item.setAttribute('aria-pressed', String(item === button));
    }
    filter();
  });
  input?.addEventListener('input', filter);
  document.getElementById('siteSearch')?.addEventListener('submit', event => {
    event.preventDefault(); filter();
    document.getElementById('fresh')?.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
  });
  filter();
})();
