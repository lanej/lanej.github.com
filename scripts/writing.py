"""Local drafts -> reviewed Markdown bundles. Never commits, pushes, or deploys."""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def valid_slug(slug):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Use a lowercase slug with letters, digits, and single hyphens.')
    return slug


def now():
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def create_draft(root, slug, title):
    valid_slug(slug)
    if not title.strip():
        raise ValueError('A title is required.')
    if (root / 'content' / 'writing' / slug).exists():
        raise FileExistsError('This published slug already exists.')
    folder = root / 'drafts' / slug
    folder.mkdir(parents=True, exist_ok=False)
    text = f'+++\ntitle = {json.dumps(title, ensure_ascii=False)}\ndescription = ""\ndate = "{now()}"\ndraft = true\ntoc = false\n+++\n\n'
    path = folder / 'index.md'
    path.write_text(text, encoding='utf-8')
    return path


def parse_post(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('+++\n'):
        raise ValueError('Expected TOML front matter between +++ delimiters.')
    front, separator, body = text[4:].partition('\n+++\n')
    if not separator:
        raise ValueError('Missing closing +++ delimiter.')
    return tomllib.loads(front), front, body


def prepare_post(root, slug):
    valid_slug(slug)
    source = root / 'drafts' / slug
    target = root / 'content' / 'writing' / slug
    if target.exists():
        raise FileExistsError('Refusing to overwrite an existing published bundle.')
    if source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Draft bundles must not contain symlinks.')
    metadata, front, body = parse_post(source / 'index.md')
    for field in ('title', 'description'):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise ValueError(f'Add a nonempty {field} before publishing.')
    if not body.strip():
        raise ValueError('The article body is empty.')
    if metadata.get('draft') is not True:
        raise ValueError('Expected draft = true in the local draft.')
    front = re.sub(r'(?m)^draft\s*=.*$', 'draft = false', front, count=1)
    front = re.sub(r'(?m)^date\s*=.*$', f'date = "{now()}"', front, count=1)
    # Copy first, then remove the local draft only after the prepared file is written.
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    try:
        (target / 'index.md').write_text('+++\n' + front + '\n+++\n' + body, encoding='utf-8')
    except Exception:
        shutil.rmtree(target)
        raise
    shutil.rmtree(source)
    return target / 'index.md'


def hugo_binary(root):
    configured = os.environ.get('HUGO_BIN')
    if configured:
        return str(Path(configured).resolve())
    installed = root / '.tools' / 'hugo'
    if installed.exists():
        return str(installed)
    binary = shutil.which('hugo')
    if not binary:
        raise FileNotFoundError('Install the Hugo version in .hugo-version first.')
    return binary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    new = sub.add_parser('new', help='Create an ignored local draft bundle')
    new.add_argument('slug')
    new.add_argument('--title', required=True)
    sub.add_parser('preview', help='Preview the site and local drafts on loopback only')
    publish = sub.add_parser('publish', help='Prepare a reviewed draft for a normal Git PR')
    publish.add_argument('slug')
    args = parser.parse_args()
    try:
        if args.command == 'new':
            print(create_draft(ROOT, args.slug, args.title))
        elif args.command == 'publish':
            print(prepare_post(ROOT, args.slug))
            print('Prepared for publication; not deployed. Review the bundle, commit, open a PR, and merge after checks.')
        else:
            (ROOT / 'drafts').mkdir(exist_ok=True)
            command = [hugo_binary(ROOT), 'server', '--config', 'hugo.toml,hugo.preview.toml', '--buildDrafts', '--buildFuture', '--bind', '127.0.0.1', '--noHTTPCache']
            subprocess.run(command, cwd=ROOT, check=True)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
