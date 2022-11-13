"""Process mining (Finnish prosessilouhinta) from eventlogs. Version and init interface."""
from typing import List

# [[[fill git_describe()]]]
__version__ = '2022.11.13+parent.2f7619f1'
# [[[end]]] (checksum: 70f1fa44baea28ff9875ca6889b04c63)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
__all__: List[str] = []
