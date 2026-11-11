"""Validate the pinned Zellij client documentation mount."""
import sys
from pathlib import Path

from project_docs import validate

PREVIEW_ROUTES = ('/zellij-client.nvim/', '/zellij-client.nvim/reference/client/')


def main(root):
    validate(root, '/zellij-client.nvim/', Path('.zellij-client-version').read_text().strip(),
             ('getting-started/index.html', 'reference/client/index.html', 'reference/protobuf/index.html'))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
