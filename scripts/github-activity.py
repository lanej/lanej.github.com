"""Refresh a dated snapshot of GitHub's public contribution calendar, without credentials."""
import argparse
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

SOURCE = 'https://github.com/users/lanej/contributions'
SNAPSHOT = Path('data/github_activity.json')


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.counts = {}
        self.target = None
        self.label = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and 'data-date' in attrs:
            day = date.fromisoformat(attrs['data-date']).isoformat()
            level = int(attrs['data-level'])
            if level not in range(5) or day in [d['date'] for d in self.cells.values()]:
                raise ValueError('Invalid or duplicate calendar day')
            self.cells[attrs['id']] = {'date': day, 'level': level}
        if tag == 'tool-tip':
            self.target, self.label = attrs.get('for'), ''

    def handle_data(self, data):
        if self.target:
            self.label += data

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.target:
            match = re.match(r'\s*(No|[\d,]+) contributions? on ', self.label)
            if match:
                self.counts[self.target] = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            self.target = None


def snapshot(html):
    parser = Calendar()
    parser.feed(html)
    days = []
    for key, day in parser.cells.items():
        if key not in parser.counts:
            raise ValueError('Calendar count missing')
        count = parser.counts[key]
        if (count == 0) != (day['level'] == 0):
            raise ValueError('Calendar count and intensity disagree')
        days.append(dict(day, count=count))
    days.sort(key=lambda d: d['date'])
    if not 365 <= len(days) <= 371 or date.fromisoformat(days[0]['date']).weekday() != 6:
        raise ValueError('Incomplete annual calendar')
    for before, after in zip(days, days[1:]):
        if date.fromisoformat(after['date']) - date.fromisoformat(before['date']) != timedelta(days=1):
            raise ValueError('Calendar has a date gap')
    return {'source': SOURCE, 'profile': 'https://github.com/lanej',
            'retrieved': datetime.now(timezone.utc).isoformat(),
            'start': days[0]['date'], 'end': days[-1]['date'],
            'total': sum(d['count'] for d in days), 'days': days}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, help='Parse a saved public calendar instead of fetching')
    args = parser.parse_args()
    try:
        if args.html:
            html = args.html.read_text()
        else:
            request = Request(SOURCE, headers={'User-Agent': 'lanej.io-public-activity'})
            with urlopen(request, timeout=20) as response:
                html = response.read().decode()
        data = snapshot(html)
        SNAPSHOT.write_text(json.dumps(data, indent=2) + '\n')
        print(f"Public GitHub calendar: {len(data['days'])} days through {data['end']}")
    except (OSError, ValueError, KeyError) as error:
        if not SNAPSHOT.exists():
            raise
        print(f'Keeping dated GitHub activity snapshot: {error}')


if __name__ == '__main__':
    main()
