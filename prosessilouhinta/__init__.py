"""Process mining (Finnish prosessilouhinta) from eventlogs. Version and init interface."""
from typing import List

# [[[fill git_describe()]]]
__version__ = '2022.9.21+parent.339872ae'
# [[[end]]] (checksum: 8494bc4af92413e2f783961b0b7192d2)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
__all__: List[str] = []
