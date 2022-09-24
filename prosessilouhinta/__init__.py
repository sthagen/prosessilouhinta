"""Process mining (Finnish prosessilouhinta) from eventlogs. Version and init interface."""
from typing import List

# [[[fill git_describe()]]]
__version__ = '2022.9.24+parent.c701f999'
# [[[end]]] (checksum: b7ecf16b869e85e50c9e3e73bcf36510)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
__all__: List[str] = []
