/* Progressive enhancement: published Markdown endnotes remain the fallback. */
(() => {
  'use strict';

  // A citation's evidence can support a passage without underlining the passage.
  // Prefer a short authored work title or author; never manufacture source metadata.
  function citationPhrase(scope, note) {
    const text = scope.toString();
    const fragment = scope.cloneContents();
    const compact = value => value.trim().replace(/\s+/g, ' ');
    const short = value => value && value.length <= 64 && value.split(/\s+/).length <= 6;
    const candidates = [];
    const add = value => {
      value = compact(value || '');
      if (short(value) && !candidates.includes(value)) candidates.push(value);
    };
    const titles = [...note.querySelectorAll('strong a, cite, em')]
      .map(el => compact(el.textContent));

    // Short, emphasized titles already present in the prose take precedence.
    for (const el of fragment.querySelectorAll('cite, em')) {
      const value = compact(el.textContent);
      if (titles.some(title => title.toLocaleLowerCase().includes(value.toLocaleLowerCase()))) add(value);
    }
    titles.forEach(add);

    // Optional author/year format: **[Title](url)** <br> Author Name · Year.
    // Read the authored author field literally, not by guessing from prose notes.
    const first = note.firstElementChild;
    if (first?.matches('p') && first.firstElementChild?.matches('strong')) {
      const metadata = first.cloneNode(true);
      metadata.querySelector('strong')?.remove();
      metadata.querySelectorAll('.footnote-backref').forEach(el => el.remove());
      add(metadata.textContent.split('·')[0]);
    }

    // Map offsets back into the original DOM, preserving emphasis and punctuation.
    const root = scope.commonAncestorContainer;
    const nodes = [];
    if (root.nodeType === Node.TEXT_NODE) nodes.push(root);
    else {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      while (walker.nextNode()) if (scope.intersectsNode(walker.currentNode)) nodes.push(walker.currentNode);
    }
    const pieces = [];
    let length = 0;
    for (const node of nodes) {
      const start = node === scope.startContainer ? scope.startOffset : 0;
      const end = node === scope.endContainer ? scope.endOffset : node.length;
      if (end <= start) continue;
      pieces.push({node, start, end, offset: length});
      length += end - start;
    }
    if (length !== text.length) return null;

    function select(start, end) {
      const a = pieces.find(p => start >= p.offset && start < p.offset + p.end - p.start);
      const b = pieces.find(p => end > p.offset && end <= p.offset + p.end - p.start);
      if (!a || !b) return null;
      const range = document.createRange();
      range.setStart(a.node, a.start + start - a.offset);
      range.setEnd(b.node, b.start + end - b.offset);
      const selected = range.cloneContents();
      // Never hijack an ordinary link, clone an ID, or nest interactive controls.
      const interactive = 'a,button,input,select,textarea,[role="button"],.citation-related';
      if (selected.querySelector(interactive + ',[id]') ||
          a.node.parentElement?.closest(interactive) || b.node.parentElement?.closest(interactive)) return null;
      return range;
    }

    for (const value of candidates) {
      const pattern = value.split(/\s+/).map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s+');
      const match = new RegExp(pattern, 'iu').exec(text);
      if (!match) continue;
      // Do not match a title inside another word (e.g. "Go" in "Google").
      if (/[\p{L}\p{N}]/u.test(text[match.index - 1] || '') ||
          /[\p{L}\p{N}]/u.test(text[match.index + match[0].length] || '')) continue;
      const range = select(match.index, match.index + match[0].length);
      if (range && short(compact(range.toString()))) return range;
    }

    // Unstructured notes still work automatically: use a few words immediately
    // before the marker, not a sentence or everything since the last citation.
    const words = [...text.matchAll(/\S+/g)];
    for (let count = Math.min(4, words.length); count > 0; count--) {
      const start = words[words.length - count].index;
      const end = words.at(-1).index + words.at(-1)[0].length;
      if (!short(compact(text.slice(start, end)))) continue;
      const range = select(start, end);
      if (range) return range;
    }
    return null;
  }

  function initialize() {
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
    function anchorFor(entry) { return entry.anchor || entry.trigger; }
    function place(entry) {
      const {card} = entry;
      const anchor = anchorFor(entry);
      if (!anchor || !card.matches(':popover-open')) return;
      const view = viewport();
      const rect = anchor.getBoundingClientRect();
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
      close.textContent = '×';
      header.append(label, close);
      const content = document.createElement('div');
      content.className = 'citation-content';
      for (const node of note.childNodes) content.append(node.cloneNode(true));
      content.querySelectorAll('.footnote-backref, [role="doc-backlink"]').forEach(el => el.remove());
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
      const title = content.querySelector('strong a, cite, em, a[href]');
      heading.textContent = title?.textContent.trim() || `Note ${number}`;
      card.setAttribute('aria-labelledby', heading.id);
      const first = content.firstElementChild;
      if (first?.matches('p') && first.firstElementChild?.matches('strong') &&
          first.textContent.trimStart().startsWith(first.firstElementChild.textContent.trim())) {
        const strong = first.firstElementChild;
        if (strong.querySelector('a') === title) {
          strong.remove();
          while (first.firstChild && (first.firstChild.nodeName === 'BR' ||
                 (first.firstChild.nodeType === Node.TEXT_NODE && !first.firstChild.textContent.trim()))) first.firstChild.remove();
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
      card.querySelectorAll('a[href]').forEach(link => { if (!link.hasAttribute('tabindex')) link.tabIndex = 0; });
      document.body.append(card);
      const entry = {card, trigger: null, anchor: null};
      const dismissToReference = () => { card.hidePopover(); entry.trigger?.focus({preventScroll: true}); };
      close.addEventListener('click', dismissToReference);
      card.addEventListener('keydown', event => {
        if (event.defaultPrevented) return;
        if (event.key === 'Escape') {
          event.preventDefault(); event.stopPropagation(); dismissToReference(); return;
        }
        if (event.key !== 'Tab' || event.altKey || event.ctrlKey || event.metaKey) return;
        const controls = [...card.querySelectorAll('button, a[href], [tabindex]')]
          .filter(el => el.tabIndex >= 0 && !el.disabled && el.getClientRects().length);
        const index = controls.indexOf(document.activeElement);
        const next = index >= 0 ? controls[index + (event.shiftKey ? -1 : 1)] : null;
        if (!next) return;
        event.preventDefault();
        next.focus({preventScroll: true});
        const bounds = card.getBoundingClientRect();
        const target = next.getBoundingClientRect();
        if (target.top < bounds.top + 8) card.scrollTop += target.top - bounds.top - 8;
        else if (target.bottom > bounds.bottom - 8) card.scrollTop += target.bottom - bounds.bottom + 8;
      });
      card.addEventListener('beforetoggle', event => { if (event.newState === 'open') card.removeAttribute('data-positioned'); });
      card.addEventListener('toggle', () => {
        if (card.matches(':popover-open')) {
          current = entry; place(entry); close.focus({preventScroll: true});
        } else if (current === entry) current = null;
      });
      return entry;
    }

    const links = [...article.querySelectorAll('a.footnote-ref[href^="#"]')];
    links.forEach((link, index) => {
      let target;
      try { target = decodeURIComponent(link.hash.slice(1)); } catch { return; }
      const note = document.getElementById(target);
      if (!note || !note.closest('.footnotes')) return;
      const number = link.textContent.trim();
      if (!cards.has(target)) cards.set(target, makeCard(note, number));
      const entry = cards.get(target);
      const shell = link.closest('sup') || link;
      const block = link.closest('p, li, dd, blockquote');
      let related = null;
      if (block && shell !== block) {
        const previous = links.slice(0, index).reverse().find(candidate => block.contains(candidate));
        const previousShell = previous ? (previous.closest('sup') || previous) : null;
        const scope = document.createRange();
        try {
          if (previousShell && block.contains(previousShell)) scope.setStartAfter(previousShell);
          else scope.setStart(block, 0);
          scope.setEndBefore(shell);
          const range = citationPhrase(scope, note);
          if (range) {
            related = document.createElement('span');
            related.className = 'citation-related';
            related.append(range.extractContents());
            range.insertNode(related);
          }
        } catch { related = null; }
      }
      const trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'citation-toggle';
      trigger.textContent = number;
      if (link.id) trigger.id = link.id;
      trigger.setAttribute('aria-label', `Read source note ${number}: ${entry.card.querySelector('.citation-title').textContent}`);
      trigger.setAttribute('aria-haspopup', 'dialog');
      trigger.setAttribute('popovertarget', entry.card.id);
      if (related) {
        related.before(trigger);
        related.addEventListener('click', event => { if (!event.target.closest('a, button')) trigger.click(); });
        related.addEventListener('pointerenter', () => related.classList.add('citation-related-active'));
        related.addEventListener('pointerleave', () => related.classList.remove('citation-related-active'));
        shell.classList.add('citation-fallback-shell');
      } else {
        // Consecutive notes or a passage made entirely of an ordinary link must
        // still expose a usable citation, without hijacking the link or a badge.
        trigger.classList.add('citation-text-fallback');
        trigger.textContent = 'source';
        shell.before(trigger);
        shell.classList.add('citation-fallback-shell');
      }
      trigger.addEventListener('click', () => {
        if (entry.card.matches(':popover-open') && entry.trigger !== trigger) entry.card.hidePopover();
        entry.trigger = trigger;
        entry.anchor = related || trigger;
        trigger.focus({preventScroll: true});
        requestAnimationFrame(() => place(entry));
      });
      link.removeAttribute('id');
      link.classList.add('citation-fallback');
    });
    article.dataset.citationsReady = 'true';
    const reposition = () => {
      if (!current) return;
      const anchor = anchorFor(current);
      if (!anchor) return;
      const r = anchor.getBoundingClientRect();
      const v = viewport();
      if (r.bottom < v.top || r.top > v.top + v.height) current.card.hidePopover();
      else place(current);
    };
    window.addEventListener('resize', reposition, {passive: true});
    window.addEventListener('scroll', reposition, {passive: true});
    window.visualViewport?.addEventListener('resize', reposition, {passive: true});
  }
  if (document.readyState === 'complete') initialize();
  else window.addEventListener('load', initialize, {once: true});
})();
