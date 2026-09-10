"""Interaction, tablet composition, metadata, and enlarged-text regressions."""
import io
import json
from urllib.parse import urlsplit
from PIL import Image
from header_checks import verify_header
from citation_checks import verify_citations


def verify_polish(page, width, route, out, engine, label):
    result = {'header': verify_header(page, width)}
    if width in (320, 390, 1440):
        page.locator('.site-header').screenshot(path=str(out/f'{engine}-{width}-{label}-header.png'))

    if route == '/' and 700 < width <= 1000:
        portrait = page.locator('.hero-portrait').bounding_box()
        copy = page.locator('.hero-copy').bounding_box()
        assert 159 <= portrait['width'] <= 161, 'Tablet portrait dominates the introduction'
        assert copy['width'] > portrait['width'], 'Tablet copy is narrower than the portrait'
        if page.locator('.home-writing').count():
            heading = page.locator('.home-writing .section-heading').bounding_box()
            essays = page.locator('.essay-list').bounding_box()
            assert essays['y'] >= heading['y'] + heading['height'], 'Tablet essays need a single column'
        result['tablet_portrait_width'] = portrait['width']

    if route == '/':
        background = page.locator('.background-section')
        assert 'UPS' in background.inner_text(), 'Operational background is missing'
        assert background.locator('a[href="/record/#early-career"]').count() == 1

    if route == '/record/':
        links = page.locator('.work-index a')
        expected = {'#easypost-technology-strategy', '#fastly', '#engine-yard', '#early-career', '#sapporo-rubykaigi-2012', '#open-source'}
        anchors = links.evaluate_all('(links) => links.map(a => a.getAttribute("href"))')
        assert len(anchors) == len(expected) and set(anchors) == expected, 'Missing or duplicate Work section links'
        for index, anchor in enumerate(anchors):
            target = page.locator(anchor)
            assert target.count() == 1, f'Broken section link: {anchor}'
            links.nth(index).click()
            assert page.url.endswith(anchor), f'Section link failed: {anchor}'
            assert target.is_visible(), f'Section is hidden: {anchor}'
        result['section_links'] = anchors
        earlier = page.locator('.career-timeline')
        assert earlier.locator(':scope > .career-company').count() == 7, 'Keep all seven employers grouped'
        assert earlier.locator('.company-logo img').count() == 7, 'Use one logo per employer'
        assert earlier.locator('[data-company="easypost"] .career-roles > li').count() == 7, 'Preserve the EasyPost role progression'
        for company in ('HubSpot', '3M / Brontes Technologies', 'EMC', 'UPS'):
            assert company in earlier.inner_text(), f'Missing earlier employer: {company}'
        assert 'Quality Engineering Co-op' in earlier.inner_text(), 'Preserve the EMC co-op title'
        result['earlier_work_verified'] = True

    if route == '/about/':
        biography = page.locator('.prose').first.inner_text()
        for company in ('UPS', 'EMC', '3M', 'Brontes Technologies', 'HubSpot', 'Engine Yard', 'Fastly', 'EasyPost'):
            assert company in biography, f'Missing career context: {company}'
        assert 'package handler and then a supervisor' in biography, 'Preserve the operational starting point'
        resources = page.locator('details.speaker-resources')
        assert resources.count() == 1 and resources.get_attribute('open') is None
        assert page.locator('#contact').count() == 1
        assert not page.locator('.speaker-resources #contact').count(), 'Contact must not be collapsed'
        summary = resources.locator('summary')
        summary.focus()
        page.keyboard.press('Enter')
        assert resources.get_attribute('open') is not None, 'Speaker resources did not open with keyboard'
        photo = resources.locator('a[download="josh-lane-headshot.jpg"]')
        assert photo.count() == 1 and photo.is_visible()
        assert resources.locator('h2').inner_text() == 'Short biography'
        assert 'supervision at UPS' in resources.inner_text(), 'Speaker biography lost operational context'
        if width in (390, 1440):
            resources.screenshot(path=str(out/f'{engine}-{width}-speaker-resources-open.png'))
        summary.focus()
        page.keyboard.press('Space')
        assert resources.get_attribute('open') is None, 'Speaker resources did not close with keyboard'
        result['speaker_resources_keyboard'] = 'passed'
        result['operations_to_technology_context'] = True

    # A captioned Markdown image is a figure, never a figure nested in a paragraph.
    assert not page.locator('p > figure.article-figure').count(), 'Invalid block figure within paragraph'
    result['visible_image_captions'] = page.locator('.article-figure figcaption').all_text_contents()
    for caption in page.locator('.article-figure figcaption').all():
        assert caption.is_visible() and caption.inner_text().strip(), 'Missing visible caption'

    image_url = page.locator('meta[property="og:image"]').get_attribute('content')
    image_parts = urlsplit(image_url)
    canonical = urlsplit(page.locator('link[rel="canonical"]').get_attribute('href'))
    assert image_parts.scheme in ('http', 'https') and image_parts.netloc, 'Social image URL must be absolute'
    assert (image_parts.scheme, image_parts.netloc) == (canonical.scheme, canonical.netloc), 'Social image must use the canonical site origin'
    actual_origin = urlsplit(page.url)
    fetch_url = image_url
    # A production build keeps lanej.io canonical metadata during local testing.
    # Fetch its asset path from the local artifact, not an older live deployment.
    # Live-domain checks still request the exact public image URL without rewriting.
    if actual_origin.hostname in ('127.0.0.1', 'localhost', '::1'):
        fetch_url = image_parts._replace(scheme=actual_origin.scheme, netloc=actual_origin.netloc).geturl()
    else:
        assert (actual_origin.scheme, actual_origin.netloc) == (canonical.scheme, canonical.netloc), 'Browser is not on the canonical site'
    response = page.context.request.get(fetch_url)
    assert response.ok, f'Social image does not resolve: HTTP {response.status} {fetch_url} (metadata: {image_url})'
    with Image.open(io.BytesIO(response.body())) as image:
        image.load()
        assert image.width == int(page.locator('meta[property="og:image:width"]').get_attribute('content'))
        assert image.height == int(page.locator('meta[property="og:image:height"]').get_attribute('content'))
    assert page.locator('meta[property="og:image:alt"]').get_attribute('content')
    assert page.locator('meta[name="twitter:image"]').get_attribute('content') == image_url
    structured = [json.loads(text) for text in page.locator('script[type="application/ld+json"]').all_text_contents()]
    person = next(item for item in structured if item.get('@type') == 'Person')
    assert 'josh-lane' in person['image'], 'An article image replaced the Person portrait'
    for item in structured:
        if item.get('@type') == 'BlogPosting':
            assert item['image'] == image_url, 'Article social and structured images differ'
    result['social_image'] = image_url
    result['social_image_verified_url'] = fetch_url

    # Reflow is a separate acceptance criterion: enlarged text may extend below
    # the first viewport, but must never be shrunk, clipped, or hidden to fit it.
    if width in (320, 390, 768, 1440):
        page.evaluate('''() => {
            window.scrollTo(0, 0);
            document.documentElement.style.fontSize = '200%';
            document.querySelectorAll('details').forEach(el => el.open = true);
        }''')
        metrics = page.evaluate('''() => ({
            width: innerWidth, scrollWidth: document.documentElement.scrollWidth,
            rootFont: parseFloat(getComputedStyle(document.documentElement).fontSize),
            clipped: [...document.querySelectorAll('h1,h2,h3,h4,summary,.flow-node,.feedback-label,figcaption,.site-header nav a')]
                .filter(el => el.getBoundingClientRect().width > 0 && el.scrollWidth > el.clientWidth + 2)
                .map(el => ({tag:el.tagName,text:el.textContent.trim(),width:el.clientWidth,scrollWidth:el.scrollWidth}))
        })''')
        metrics['header'] = verify_header(page, width, allow_wrap=True)
        if width in (320, 768):
            page.screenshot(path=str(out/f'{engine}-{width}-{label}-text-200.png'),full_page=False,scale='css')
        assert metrics['rootFont'] >= 32, 'Enlarged-text test did not enlarge text'
        assert metrics['scrollWidth'] <= width + 1, f'200% text causes page overflow: {engine} {width} {route}: {metrics}'
        assert not metrics['clipped'], f'200% text is clipped: {engine} {width} {route}: {metrics["clipped"]}'
        result['text_scale_200'] = metrics
        page.evaluate('''() => {
            document.documentElement.style.removeProperty('font-size');
            document.querySelectorAll('details').forEach(el => el.open = false);
        }''')
    result['citations'] = verify_citations(page, width, route, out, engine, label)
    page.evaluate('window.scrollTo(0,0)')
    return result
