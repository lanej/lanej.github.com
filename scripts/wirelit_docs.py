"""Validate the pinned Wirelit documentation mount."""
import sys
from pathlib import Path

from project_docs import validate

PREVIEW_ROUTES = (
    '/wirelit/',
    '/wirelit/reference/api/services/shipping-v1-shipmentservice/getshipment/',
)


def main(root):
    validate(root, '/wirelit/', Path('.wirelit-version').read_text().strip(),
             ('reference/api/services/shipping-v1-shipmentservice/getshipment/index.html',))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
