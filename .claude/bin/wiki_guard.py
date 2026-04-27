#!/usr/bin/env python3
from __future__ import annotations

import wiki_guard_lib.core as _core

for _name in _core.__all__:
    globals()[_name] = getattr(_core, _name)


if __name__ == "__main__":
    raise SystemExit(_core.main())
