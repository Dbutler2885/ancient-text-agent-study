// Shared tabs for inspection tools and methodology. Reading-version tabs retain
// their own query-string state and generated text in interpretation.js.
const sectionTabGroups = [
  { id: 'evidence-tabs', panels: [['case-panel', 'Disputed readings'], ['inspection', 'Pixel inspection'], ['word-analysis', 'Word boundaries'], ['text-location', 'Passage locations']] },
  { id: 'method-tabs', panels: [['reasoning-method', 'Reasoning and hypotheses'], ['software-method', 'Software and limits']] },
];
function selectSectionTab(group, panelId) {
  const tablist = document.getElementById(group.id);
  group.panels.forEach(([id], index) => {
    const selected = id === panelId;
    const panel = document.getElementById(id);
    const tab = document.getElementById('tab-' + id);
    panel.hidden = !selected;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
    if (selected) tablist.style.setProperty('--active-tab', index);
  });
}
function revealSectionTarget(id) {
  const target = document.getElementById(id);
  if (!target) return false;
  const panel = target.closest('[data-section-panel]');
  if (!panel) return false;
  const group = sectionTabGroups.find(item => item.panels.some(([key]) => key === panel.id));
  selectSectionTab(group, panel.id);
  // Open nested evidence disclosures when a link points inside one.
  for (let node = target.parentElement; node && node !== panel; node = node.parentElement) {
    if (node.tagName === 'DETAILS') node.open = true;
  }
  return true;
}
for (const group of sectionTabGroups) {
  const tablist = document.getElementById(group.id);
  tablist.style.setProperty('--tab-count', group.panels.length);
  group.panels.forEach(([id, label], index) => {
    const tab = document.createElement('button');
    tab.type = 'button'; tab.className = 'reading-tab'; tab.id = 'tab-' + id;
    tab.textContent = label; tab.setAttribute('role', 'tab'); tab.setAttribute('aria-controls', id);
    const panel = document.getElementById(id);
    panel.dataset.sectionPanel = group.id;
    panel.setAttribute('role', 'tabpanel'); panel.setAttribute('aria-labelledby', tab.id); panel.tabIndex = 0;
    tab.onclick = () => {
      selectSectionTab(group, id);
      if (location.hash !== '#' + id) history.pushState(null, '', '#' + id);
    };
    tab.onkeydown = event => {
      let next;
      if (event.key === 'ArrowRight') next = (index + 1) % group.panels.length;
      else if (event.key === 'ArrowLeft') next = (index - 1 + group.panels.length) % group.panels.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = group.panels.length - 1;
      else return;
      event.preventDefault();
      const button = tablist.children[next]; button.focus(); button.click();
    };
    tablist.append(tab);
  });
  selectSectionTab(group, group.panels[0][0]);
  requestAnimationFrame(() => requestAnimationFrame(() => tablist.classList.add('tabs-ready')));
}
function revealHashTarget() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  if (revealSectionTarget(id)) document.getElementById(id).scrollIntoView();
}
// Reveal before the browser performs its native anchor navigation.
document.addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  if (!link) return;
  try { revealSectionTarget(decodeURIComponent(link.hash.slice(1))); } catch { /* Invalid fragment. */ }
}, true);
window.addEventListener('hashchange', revealHashTarget);
window.addEventListener('popstate', revealHashTarget);
revealHashTarget();
