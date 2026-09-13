"""One regression for parsing, completeness, and preservation of a dated snapshot."""
import importlib.util
from pathlib import Path
from datetime import date, timedelta
from tempfile import TemporaryDirectory
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('activity', Path(__file__).with_name('github-activity.py'))
activity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activity)
fixture = Path('scripts/fixtures/github-calendar.html').read_text()
parser = activity.Calendar()
parser.feed(fixture)
assert parser.counts == {'day-a': 0, 'day-b': 1234}
assert parser.cells['day-b'] == {'date': '2026-09-13', 'level': 4}
# Expand the fixture's date/ID values into a full year; no large inline HTML fixture.
start = date(2025, 9, 14)
cell = fixture[fixture.index('<td id="day-a"'):fixture.index('<td id="day-b"')]
label = fixture[fixture.index('<tool-tip for="day-a"'):fixture.index('<tool-tip for="day-b"')]
complete = ''.join(
    (cell + label).replace('2026-09-12', (start + timedelta(days=i)).isoformat())
    .replace('day-a', f'day-{i}')
    for i in range(365)
)
data = activity.snapshot(complete)
assert len(data['days']) == 365 and data['total'] == 0
for invalid in (fixture, complete.replace('2025-09-15', '2025-09-14'), complete.replace('No contributions', 'Unknown', 1)):
    try:
        activity.snapshot(invalid)
        raise AssertionError('Invalid calendar accepted')
    except ValueError:
        pass
with TemporaryDirectory() as tmp:
    target = Path(tmp) / 'snapshot.json'
    target.write_text('existing dated snapshot')
    with patch.object(activity, 'SNAPSHOT', target), patch.object(activity, 'urlopen', side_effect=OSError('unavailable')), patch('sys.argv', ['github-activity.py']):
        activity.main()
    assert target.read_text() == 'existing dated snapshot'
print('Passed: counts, complete calendar, malformed data, and retained snapshot on fetch failure.')
