"""Derive the license information and publish in docs."""
import functools
import json
import pathlib
import pkg_resources
import string
import subprocess  # nosec
from typing import List, Tuple

__all__ = ['dependency_tree_console_text', 'direct_dependencies_table', 'indirect_dependencies_table']

ENCODING = 'utf-8'
TP_PATH = pathlib.Path('docs', 'third-party')

TABLE_KEYS = (('Name', 'URL'), 'Version', 'License', 'Author', 'Description')
HEADER_LABELS = ('Name', 'Version', 'License', 'Author', 'Description (from packaging data)')
FALLBACK_URLS = {
    'typing-extensions': 'https://github.com/python/typing/blob/master/typing_extensions/README.rst',
}
TARGET = """\
__version__ = '$version$+parent.$revision$'\
"""


@functools.lru_cache()
def _fetch_direct_dependency_names():
    with pathlib.Path('requirements.txt').open(encoding=ENCODING) as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


def _generate_dependency_information() -> None:
    """Use pip-licenses for creation of diverse databases and graphs."""
    install_requires = _fetch_direct_dependency_names()
    tokens = set(list(string.ascii_letters + '-_'))
    direct_names = [''.join(c for c in term if c in tokens) for term in install_requires]
    direct_vector = [
        'pip-licenses', '--format', 'json', '-p', *direct_names,
        '--with-authors', '--with-description', '--with-urls', '--with-license-file', '--with-notice-file',
        '--output-file', str(TP_PATH / 'direct-dependency-licenses.json')]
    noise = subprocess.run(direct_vector, capture_output=True, encoding=ENCODING, text=True, check=True).stdout.strip()  # nosec
    if not noise.startswith('created path: ') or not noise.endswith('direct-dependency-licenses.json'):
        raise RuntimeError(noise)

    indirect_names = [  # TODO(sthagen) these indirect deps may diverge ...
        'click',

    ]
    full_vector = [
        'pip-licenses', '--format', 'json', '-p', *direct_names, *indirect_names,
        '--with-authors', '--with-description', '--with-urls', '--with-license-file', '--with-notice-file',
        '--output-file', str(TP_PATH / 'all-dependency-licenses.json')]
    noise = subprocess.run(full_vector, capture_output=True, encoding=ENCODING, text=True, check=True).stdout.strip()  # nosec
    if not noise.startswith('created path: ') or not noise.endswith('all-dependency-licenses.json'):
        raise RuntimeError(noise)

    base_vector = ['pipdeptree', '--packages', ','.join(direct_names)]
    jobs = (
        (TP_PATH / 'package-dependency-tree.dot.txt', base_vector + ['--graph-output', 'dot']),
        (TP_PATH / 'package-dependency-tree.svg', base_vector + ['--graph-output', 'svg']),
        (TP_PATH / 'package-dependency-tree.json', base_vector + ['--json-tree', '--warn', 'silence']),
        (TP_PATH / 'package-dependency-tree.console.txt', base_vector + ['--warn', 'silence']),
    )
    for target, vector in jobs:
        plot = subprocess.run(vector, capture_output=True, encoding=ENCODING, text=True, check=True).stdout.strip()  # nosec
        target.write_text(plot, encoding=ENCODING)


@functools.lru_cache()
def _fetch_dependencies(direct_only: bool = True):
    db = 'direct-dependency-licenses.json' if direct_only else 'all-dependency-licenses.json'
    dep_json_path = pathlib.Path('docs', 'third-party') / db
    with open(dep_json_path, 'rt', encoding=ENCODING) as handle:
        data = json.load(handle)
    return data


def _markdown_table(table: List[Tuple[str, str, str, str, str]], header_labels=HEADER_LABELS) -> str:
    """Create the gfm table as string."""
    columns = header_labels
    col_wid = {key: len(key) for key in columns}
    for record in table:
        for key, cell in zip(columns, record):
            col_wid[key] = max(len(cell), col_wid[key])

    header_cells = [key.ljust(col_wid[key]) for key in columns]
    header = f'| {" | ".join(header_cells)} |'

    separator_cells = ['-' * (col_wid[key] + 1) for key in columns]
    separator = f'|:{"|:".join(separator_cells)}|'

    rows = [f'| {" | ".join(str(v).ljust(col_wid[k]) for k, v in zip(columns, line))} |' for line in table]

    return '\n'.join([header] + [separator] + rows)


def _extract_rows(data):
    rows = []
    for record in data:
        nam = record['Name']
        url = record.get('URL', '')
        if url == 'UNKNOWN':
            url = FALLBACK_URLS.get(nam, '')
        nam_e = f'[{nam}]({url})' if url else nam

        ver = record['Version']
        ver_sion = f'[{ver}](https://pypi.org/project/{nam}/{ver}/)'
        lic = record['License']
        aut = record['Author']
        des = record['Description']
        rows.append((nam_e, ver_sion, lic, aut, des))
    rows.sort()
    return rows


def direct_dependencies_table() -> None:
    """Fill in the data from the direct dependencies."""
    _generate_dependency_information()
    print(_markdown_table(_extract_rows(_fetch_dependencies(direct_only=True))))


def indirect_dependencies_table() -> None:
    """Fill in the data from the indirect dependencies."""
    direct_data = _fetch_dependencies(direct_only=True)
    direct_names = tuple(record['Name'] for record in direct_data)
    indirect_only_data = [rec for rec in _fetch_dependencies(direct_only=False) if rec['Name'] not in direct_names]
    print(_markdown_table(_extract_rows(indirect_only_data)))


def dependency_tree_console_text():
    """Fill in the pipdeptree console output minus any warnings."""
    console_tree = (TP_PATH / 'package-dependency-tree.console.txt').read_text(encoding=ENCODING).strip()
    fence = '````'
    print(f'{fence}console')
    print(console_tree)
    print(fence)
