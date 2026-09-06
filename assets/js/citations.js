/* Progressive enhancement: the published Markdown endnotes remain the fallback. */
(() => {
  'use strict';
  if (typeof HTMLElement.prototype.showPopover !== 'function' ||
      !('popoverTargetElement' in HTMLButtonElement.prototype)) return;

  const article = document.querySelector('.article-body');
  if (!article || article.dataset.citationsReady ||
      getComputedStyle(article).getPropertyValue('--citation-previews').trim() !== 'enabled') return;
  const cards = new Map();
  let current = null;

  function viewport() {
    const view = window.visualViewport;
    return {left: view?.offsetLeft || 0, top: view?.offsetTop || 0,
      width: view?.width || innerWidth, height: view?.height || innerHeight};
  }

  function place(entry) {
    const {card, trigger} = entry;
    if (!trigger || !card.matches(':popover-open')) return;
    const view = viewport();
    const rect = trigger.getBoundingClientRect();
    const gap = 12;
    card.style.maxHeight = `${Math.max(80, view.height - gap * 2)}px`;
    card.style.width = `${Math.min(440, view.width - gap * 2)}px`;
    if (view.width <= 600) {
      card.style.maxHeight = `${Math.max(80, Math.min(480, view.height * 0.65))}px`;
      card.style.left = `${view.left + (view.width - card.offsetWidth) / 2}px`;
      card.style.top = `${view.top + view.height - card.offsetHeight - gap}px`;
    } else {
      const below = view.top + view.height - rect.bottom - gap * 2;
      const above = rect.top - view.top - gap * 2;
      const useBelow = below >= Math.min(card.offsetHeight, 220) || below >= above;
      card.style.maxHeight = `${Math.max(80, useBelow ? below : above)}px`;
      const left = Math.max(view.left + gap,
        Math.min(rect.left - 16, view.left + view.width - card.offsetWidth - gap));
      const top = useBelow ? rect.bottom + gap : rect.top - card.offsetHeight - gap;
      card.style.left = `${left}px`;
      card.style.top = `${Math.max(view.top + gap,
        Math.min(top, view.top + view.height - card.offsetHeight - gap))}px`;
    }
    card.dataset.positioned = 'true';
  }

  function makeCard(note, number) {
    const card = document.createElement('section');
    card.id = `citation-preview-${cards.size + 1}`;
    card.className = 'citation-popover';
    card.setAttribute('popover', 'auto');
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-modal', 'false');

    const header = document.createElement('header');
    header.className = 'citation-header';
    const label = document.createElement('p');
    label.className = 'citation-label';
    label.textContent = `Source note ${number}`;
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'citation-close';
    close.setAttribute('aria-label', 'Close citation');
    close.setAttribute('autofocus', '');
    close.textContent = '×';
    header.append(label, close);

    const content = document.createElement('div');
    content.className = 'citation-content';
    for (const node of note.childNodes) content.append(node.cloneNode(true));
    content.querySelectorAll('.footnote-backref, [role="doc-backlink"]').forEach(el => el.remove());
    // Preserve complex notes without introducing duplicate document IDs.
    const ids = new Map();
    content.querySelectorAll('[id]').forEach(el => {
      const old = el.id;
      el.id = `${card.id}-${old}`;
      ids.set(old, el.id);
    });
    content.querySelectorAll('[href],[for],[aria-labelledby],[aria-describedby]').forEach(el => {
      for (const attr of ['for', 'aria-labelledby', 'aria-describedby']) {
        if (el.hasAttribute(attr)) el.setAttribute(attr,
          el.getAttribute(attr).split(/\s+/).map(id => ids.get(id) || id).join(' '));
      }
      const href = el.getAttribute('href');
      if (href?.startsWith('#') && ids.has(href.slice(1))) el.setAttribute('href', `#${ids.get(href.slice(1))}`);
    });

    const heading = document.createElement('h2');
    heading.className = 'citation-title';
    heading.id = `${card.id}-title`;
    // Use only authored text. Never guess authors, dates, or remote page titles.
    const title = content.querySelector('strong a, cite, em, a[href]');
    heading.textContent = title?.textContent.trim() || `Note ${number}`;
    card.setAttribute('aria-labelledby', heading.id);

    // Preferred Markdown: a bold linked title, author/year, then explanatory prose.
    // Legacy prose notes also work unchanged, including every source and qualification.
    const first = content.firstElementChild;
    if (first?.matches('p') && first.firstElementChild?.matches('strong') &&
        first.textContent.trimStart().startsWith(first.firstElementChild.textContent.trim())) {
      const strong = first.firstElementChild;
      if (strong.querySelector('a') === title) {
        strong.remove();
        while (first.firstChild && (first.firstChild.nodeName === 'BR' ||
               (first.firstChild.nodeType === Node.TEXT_NODE && !first.firstChild.textContent.trim()))) {
          first.firstChild.remove();
        }
        if (!first.textContent.trim()) first.remove();
        else first.classList.add('citation-metadata');
      }
    }

    const footer = document.createElement('footer');
    footer.className = 'citation-footer';
    const primary = note.querySelector('a[href]:not(.footnote-backref)');
    if (primary) {
      const source = document.createElement('a');
      source.href = primary.href;
      source.textContent = 'Open source ↗';
      footer.append(source);
    }
    const original = document.createElement('a');
    original.href = `#${note.id}`;
    original.textContent = 'Full reference ↓';
    original.addEventListener('click', () => card.hidePopover());
    footer.append(original);
    card.append(header, heading, content, footer);
    document.body.append(card);
    const entry = {card, trigger: null};
    close.addEventListener('click', () => {
      card.hidePopover();
      entry.trigger?.focus({preventScroll: true});
    });
    card.addEventListener('beforetoggle', event => {
      if (event.newState === 'open') card.removeAttribute('data-positioned');
    });
    card.addEventListener('toggle', () => {
      if (card.matches(':popover-open')) { current = entry; place(entry); }
      else if (current === entry) current = null;
    });
    return entry;
  }

  article.querySelectorAll('a.footnote-ref[href^="#"]').forEach(link => {
    let target;
    try { target = decodeURIComponent(link.hash.slice(1)); } catch { return; }
    const note = document.getElementById(target);
    if (!note || !note.closest('.footnotes')) return;
    const number = link.textContent.trim();
    if (!cards.has(target)) cards.set(target, makeCard(note, number));
    const entry = cards.get(target);
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'citation-toggle';
    trigger.textContent = number;
    if (link.id) trigger.id = link.id;
    trigger.setAttribute('aria-label', `Read source note ${number}: ${entry.card.querySelector('.citation-title').textContent}`);
    trigger.setAttribute('aria-haspopup', 'dialog');
    trigger.setAttribute('popovertarget', entry.card.id);
    trigger.addEventListener('click', () => {
      if (entry.card.matches(':popover-open') && entry.trigger !== trigger) entry.card.hidePopover();
      entry.trigger = trigger;
      // Native activation runs after this listener; position before the next paint.
      requestAnimationFrame(() => place(entry));
    });
    link.removeAttribute('id');
    link.classList.add('citation-fallback');
    link.after(trigger);
  });
  article.dataset.citationsReady = 'true';

  const reposition = () => {
    if (!current) return;
    const r = current.trigger.getBoundingClientRect();
    const v = viewport();
    if (r.bottom < v.top || r.top > v.top + v.height) current.card.hidePopover();
    else place(current);
  };
  window.addEventListener('resize', reposition, {passive: true});
  window.addEventListener('scroll', reposition, {passive: true});
  window.visualViewport?.addEventListener('resize', reposition, {passive: true});
})();
