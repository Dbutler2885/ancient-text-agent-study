const interpretation = DATA.interpretation;
const openingNote = document.querySelector(".opening-note");
openingNote.remove();
const editionModes = [
  { id: 'image', slug: 'strict', title: 'Strict transcription and translation', short: 'Only surviving text; gaps and uncertain letters stay visible.', description: 'A conservative transcription of the physical groups, with a fragmentary English translation. “Strict” describes what is included, not certainty about every letter. Underdots mark uncertain letters, […] missing material, and ◊ unreadable traces. Groups remain separate. English brackets provide grammatical help; they do not restore Hebrew words.' },
  { id: 'context', slug: 'contextual', title: 'Contextual reading and translation', short: 'Tentative completions and translation choices, with larger gaps retained.', description: 'A working Hebrew reading and English translation in likely passage order. Damaged words are tentatively completed; a few marked reference supplies help the clauses read. Larger gaps remain […]. Inference marks replace underdots here without increasing certainty.' },
  { id: 'reference', slug: 'reconstructed', title: 'Fuller reconstruction and translation', short: 'A fuller passage, with missing wording supplied from Genesis and marked.', description: 'A reference-led reconstruction of Genesis 1:1–10, including the entirely unpreserved verse 3. Blue brackets mark supplied phrases. The apparent image spellings יומם and לשמים are retained. This does not establish original line lengths, physical joins, or the extent of losses.' },
];
const provenanceNames = { observed: 'Surviving wording', inferred: 'Contextual inference', supplied: 'Reference supply' };
let renderedEditionId = null;

function editionElement(tag, className, value) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (value !== undefined) element.textContent = value;
  return element;
}
function appendSourceLinks(container, sources) {
  for (const source of sources) {
    const link = editionElement('a', '', source.label);
    link.href = source.url;
    container.append(link, document.createTextNode(' '));
  }
}
function segmentLinks(container, ids, returnId) {
  for (const id of ids) {
    const segment = DATA.findings.segments.find(item => item.id === id);
    const link = editionElement('a', '', 'Inspect the image · ' + id);
    link.href = '#inspection';
    link.onclick = () => {
      $('region').value = segment.region;
      render();
      $('return-to-reading').href = '#' + returnId;
      $('return-to-reading').textContent = 'Back to ' + (returnId.startsWith('verse-') ? 'Genesis 1:' + returnId.slice(6) : id) + ' ↑';
    };
    container.append(link);
  }
}
function hypothesisBody(hypothesis, includeConclusion = true) {
  const body = editionElement('div', 'hypothesis-body');
  const fields = includeConclusion ? [['preferred', 'Working conclusion'], ['evidence', 'Evidence'], ['alternatives', 'Alternatives'], ['limit', 'Limit']] : [['alternatives', 'Alternatives'], ['limit', 'Limit']];
  for (const [key, label] of fields) {
    const p = editionElement('p', 'small');
    p.append(editionElement('strong', '', label + ': '), document.createTextNode(hypothesis[key]));
    body.append(p);
  }
  if (hypothesis.sources.length) {
    const links = editionElement('p', 'small source-links');
    appendSourceLinks(links, hypothesis.sources);
    body.append(links);
  }
  return body;
}
function phraseText(chunk, language) {
  const span = editionElement('span', 'edition-phrase ' + chunk.kind);
  span.dataset.phrase = chunk.id;
  span.textContent = chunk.kind === 'supplied' ? '[' + chunk[language] + ']' : chunk[language];
  return span;
}
function passageNotes(passage, mode, rowId) {
  const details = editionElement('details', 'passage-notes');
  details.append(editionElement('summary', '', 'Reading notes · evidence and alternatives'));
  const body = editionElement('div', 'passage-notes-body');
  body.append(editionElement('p', 'small muted', 'These notes distinguish the Hebrew reading from its English interpretation. A phrase-level label can include both surviving and completed words.'));
  for (const chunk of passage.chunks.filter(item => mode.id === 'reference' || item.context)) {
    const record = editionElement('article', 'phrase-record');
    record.dataset.record = chunk.id;
    const heading = editionElement('div', 'record-heading');
    heading.append(editionElement('span', 'record-kind ' + chunk.kind, provenanceNames[chunk.kind]));
    const he = editionElement('span', 'record-hebrew', chunk.hebrew);
    he.lang = 'he'; he.dir = 'rtl';
    heading.append(he);
    record.append(heading, editionElement('p', 'record-english', chunk.english), editionElement('p', 'small', chunk.basis));
    if (chunk.hypothesis) record.append(hypothesisBody(interpretation.hypotheses.find(item => item.id === chunk.hypothesis), false));
    body.append(record);
  }
  if (mode.id === 'context' && passage.chunks.some(item => !item.context)) {
    body.append(editionElement('p', 'small muted', 'The […] gaps stay unfilled in this mode. Switch to Fuller reconstruction to see the reference wording and its supply notes.'));
  }
  const sourceIds = [...new Set(passage.chunks.flatMap(item => item.segments))];
  const sources = editionElement('div', 'passage-source-links');
  segmentLinks(sources, sourceIds, rowId);
  body.append(sources);
  const reference = editionElement('p', 'small source-links');
  appendSourceLinks(reference, [interpretation.reference]);
  body.append(reference);
  details.append(body);
  return details;
}
function renderEdition(mode) {
  renderedEditionId = mode.id;
  for (const tab of $('edition-modes').querySelectorAll('[role="tab"]')) {
    const selected = tab.dataset.mode === mode.id;
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
  }
  $('edition-modes').style.setProperty('--active-tab', editionModes.indexOf(mode));
  $('reading-panel').setAttribute('aria-labelledby', 'reading-tab-' + mode.id);
  text('edition-title', mode.title);
  text('edition-description', mode.description);
  $('provenance-legend').hidden = mode.id === 'image';
  $('phrase-instructions').hidden = mode.id === 'image';
  $('return-to-reading').href = '#reading-modes';
  $('return-to-reading').textContent = 'Back to the reading ↑';
  $('edition-content').replaceChildren();
  if (mode.id === 'image') {
    for (const segment of DATA.findings.segments) {
      const row = editionElement('article', 'edition-row');
      row.id = 'segment-' + segment.id;
      row.append(editionElement('h3', '', segment.id + ' · physical group'));
      const pair = editionElement('div', 'edition-pair');
      const he = editionElement('p', 'edition-hebrew reading', segment.text);
      he.lang = 'he'; he.dir = 'rtl';
      pair.append(he, editionElement('p', 'edition-english', segment.translation));
      row.append(pair, editionElement('p', 'small muted', segment.note));
      if (segment.id === "S01") row.append(openingNote.cloneNode(true));
      const links = editionElement('div', 'passage-source-links');
      segmentLinks(links, [segment.id], row.id);
      row.append(links);
      $('edition-content').append(row);
    }
    normalizeDotted();
    return;
  }
  for (const passage of interpretation.rows) {
    const row = editionElement('article', 'edition-row');
    row.id = 'verse-' + passage.verse;
    row.append(editionElement('h3', '', 'Genesis 1:' + passage.verse));
    const pair = editionElement('div', 'edition-pair');
    const he = editionElement('p', 'edition-hebrew');
    he.lang = 'he'; he.dir = 'rtl';
    const en = editionElement('p', 'edition-english');
    let previousWasGap = false;
    for (const chunk of passage.chunks) {
      if (mode.id === 'context' && !chunk.context) {
        if (!previousWasGap) {
          he.append(editionElement('span', 'edition-gap', '[…] '));
          en.append(editionElement('span', 'edition-gap', '[…] '));
        }
        previousWasGap = true;
      } else {
        he.append(phraseText(chunk, 'hebrew'), document.createTextNode(' '));
        en.append(phraseText(chunk, 'english'), document.createTextNode(' '));
        previousWasGap = false;
      }
    }
    pair.append(he, en);
    row.append(pair);
    if (passage.verse === 1) row.append(openingNote.cloneNode(true));
    for (const chunk of passage.chunks.filter(item => item.translation_decision)) row.append(editionElement('p', 'translation-note', chunk.translation_decision));
    if (passage.association) row.append(editionElement('p', 'small muted passage-association', passage.association));
    row.append(passageNotes(passage, mode, row.id));
    $('edition-content').append(row);
  }
}
const tabLabels = ['Strict transcription', 'Contextual reading', 'Fuller reconstruction'];
for (const [index, mode] of editionModes.entries()) {
  const tab = editionElement('button', 'reading-tab', tabLabels[index]);
  tab.type = 'button'; tab.dataset.mode = mode.id; tab.id = 'reading-tab-' + mode.id;
  tab.setAttribute('role', 'tab');
  tab.setAttribute('aria-label', mode.title);
  tab.setAttribute('aria-controls', 'reading-panel');
  tab.onclick = () => {
    if (renderedEditionId === mode.id) return;
    const url = new URL(location.href);
    url.searchParams.set('reading', mode.slug);
    if (/^#(?:verse-|segment-)/.test(url.hash)) url.hash = 'reading-modes';
    history.pushState(null, '', url);
    renderEdition(mode);
  };
  tab.onkeydown = event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % editionModes.length;
    else if (event.key === 'ArrowLeft') next = (index - 1 + editionModes.length) % editionModes.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = editionModes.length - 1;
    else return;
    event.preventDefault();
    const target = $('edition-modes').children[next];
    target.focus(); target.click();
  };
  $('edition-modes').append(tab);
}
for (const step of interpretation.method) $('method-chain').append(editionElement('li', '', step));
for (const hypothesis of interpretation.hypotheses) {
  const card = editionElement('article', 'hypothesis');
  card.id = 'hypothesis-' + hypothesis.id;
  card.append(editionElement('h4', '', hypothesis.title), hypothesisBody(hypothesis));
  $('hypotheses').append(card);
}
for (const statement of interpretation.search_history) $('search-history').append(editionElement('p', 'small', statement));
function renderRequestedEdition() {
  const slug = new URL(location.href).searchParams.get('reading');
  const mode = editionModes.find(item => item.slug === slug) || editionModes[0];
  if (mode.id !== renderedEditionId) renderEdition(mode);
}
window.addEventListener('popstate', renderRequestedEdition);
renderRequestedEdition();
requestAnimationFrame(() => requestAnimationFrame(() => $('edition-modes').classList.add('tabs-ready')));
