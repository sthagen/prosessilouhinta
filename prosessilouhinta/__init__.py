"""Process mining (Finnish prosessilouhinta) from eventlogs. Version and init interface."""
from typing import List

# [[[fill git_describe()]]]
__version__ = '2022.9.24+parent.87eb9a4b'
# [[[end]]] (checksum: 25667de515a0e5b7417911d2836c209d)
__version_info__ = tuple(
    e if '-' not in e else e.split('-')[0] for part in __version__.split('+') for e in part.split('.') if e != 'parent'
)
__all__: List[str] = []
