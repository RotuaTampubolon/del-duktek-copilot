from pathlib import Path

import pytest

from del_duktek_copilot.embedding.vector_store import PersistentVectorStore


def test_vector_store_requires_chromadb(tmp_path: Path, monkeypatch):
    monkeypatch.setitem(__import__("sys").modules, "chromadb", None)
    with pytest.raises(RuntimeError, match="chromadb is required"):
        PersistentVectorStore(tmp_path)


def test_vector_store_rejects_misaligned_upsert():
    store = object.__new__(PersistentVectorStore)
    store._collection = None
    with pytest.raises(ValueError, match="must align"):
        store.upsert(["a"], [[1.0], [2.0]], ["text"], [{}])


def test_vector_store_rejects_inconsistent_dimensions():
    store = object.__new__(PersistentVectorStore)
    store._collection = None
    with pytest.raises(ValueError, match="consistent positive dimension"):
        store.upsert(["a", "b"], [[1.0], [2.0, 3.0]], ["a", "b"], [{}, {}])
