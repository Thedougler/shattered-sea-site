from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


def load_wiki_guard_module() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[1]
    script_dir = repo_root / ".claude/bin"
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    module_path = repo_root / ".claude/bin/wiki_guard.py"
    spec = importlib.util.spec_from_file_location("wiki_guard", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def wiki_guard() -> ModuleType:
    return load_wiki_guard_module()
