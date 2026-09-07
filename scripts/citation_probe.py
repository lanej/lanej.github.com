"""Temporary diagnostic for citation activation, focus and screenshot side effects."""
import functools
import http.server
import json
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path('artifacts/local/citation-probe')
out.mkdir(parents=True, exist_ok=True)
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory='public'))
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f'http://127.0.0.1:{server.server_port}/writing/lead-with-problems/'
reports = []
trace = '''() => {
  window.citationTrace = [];
  const record = (type, target, extra = {}) => citationTrace.push({
    time: performance.now(), type, target: target?.id || target?.className || target?.tagName,
    active: document.activeElement?.id || document.activeElement?.className || document.activeElement?.tagName,
    y: scrollY, hash: location.hash, open: document.querySelectorAll(':popover-open').length, ...extra
  });
  for (const type of ['focusin','focusout','click','touchstart','touchend','beforetoggle','toggle'])
    document.addEventListener(type, e => record(type, e.target, {state:e.newState}), true);
  window.addEventListener('scroll', e => record('scroll', document.documentElement));
  const hide = HTMLElement.prototype.hidePopover;
  HTMLElement.prototype.hidePopover = function(...args) {
    record('hidePopover-call', this, {stack:new Error().stack});
    return hide.apply(this,args);
  };
}'''
state = '''() => ({y:scrollY,hash:location.hash,
  active:document.activeElement?.id || document.activeElement?.className || document.activeElement?.tagName,
  open:document.querySelectorAll('.citation-popover:popover-open').length})'''
try:
  with sync_playwright() as pw:
    browser = pw.webkit.launch()
    for anchor, method, activation in [(False,'none','tap'),(True,'none','tap'),(True,'viewport','tap'),(True,'document','tap'),(True,'viewport','click')]:
      label = f'{anchor}-{method}-{activation}'
      context = browser.new_context(viewport={'width':390,'height':664}, device_scale_factor=3, is_mobile=True, has_touch=True)
      page = context.new_page()
      item = {'case':label, 'samples':[]}
      try:
        page.goto(url, wait_until='networkidle')
        page.locator('img').evaluate_all('(imgs)=>Promise.all(imgs.map(i=>i.decode()))')
        page.screenshot(full_page=True, scale='css')
        if anchor:
          page.locator('.skip-link').focus()
          page.keyboard.press('Enter')
          page.locator('main').evaluate('(m)=>m.blur()')
        page.evaluate("document.documentElement.style.fontSize='200%';window.scrollTo(0,0)")
        page.evaluate('document.documentElement.scrollWidth')
        page.evaluate("document.documentElement.style.removeProperty('font-size');window.scrollTo(0,0)")
        page.evaluate(trace)
        trigger = page.locator('.citation-toggle').first
        trigger.scroll_into_view_if_needed()
        item['before'] = page.evaluate(state)
        if activation == 'tap': trigger.tap()
        else: trigger.click()
        for delay in [100,250,650]:
          page.wait_for_timeout(delay)
          item['samples'].append(page.evaluate(state))
        if method == 'viewport':
          page.screenshot(path=str(out/f'{label}.png'), full_page=False, scale='css')
        elif method == 'document':
          page.screenshot(path=str(out/f'{label}.png'), full_page=True, scale='css', clip={'x':0,'y':item['before']['y'],'width':390,'height':664})
        page.wait_for_timeout(500)
        item['after'] = page.evaluate(state)
        item['trace'] = page.evaluate('citationTrace')
        item['passed'] = all(abs(s['y']-item['before']['y']) <= 2 and s['hash']==item['before']['hash'] and s['open']==1 for s in item['samples']+[item['after']])
      except Exception as error:
        item['error'] = str(error)
        item['trace'] = page.evaluate('window.citationTrace || []')
        item['passed'] = False
      finally:
        reports.append(item)
        context.close()
    browser.close()
finally:
  server.shutdown()
  (out/'report.json').write_text(json.dumps(reports,indent=2))
print(json.dumps([{k:v for k,v in item.items() if k not in ('trace',)} for item in reports],indent=2))
assert all(item['passed'] for item in reports), 'Citation focus/snapshot probe failed; inspect artifacts/local/citation-probe/report.json'
