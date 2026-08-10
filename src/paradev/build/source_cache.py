"""Content-fingerprinted parsed-source cache for project builds."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import logging
import os
import stat as stat_module
import sys
import tempfile
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from inspect import getsourcefile
from pathlib import Path
from typing import Any, Literal, TypeVar, cast

from heavenbase.utils import cmd, dmerge, load_txt, sha256hash

from paradev.localization import canonical_language
from paradev.pdx import PDXBlock

from .loaders import (
    CollectionSourceBundle,
    CopySource,
    LocalizationEntry,
    ModuleSourceBundle,
    PDXBlockSource,
)
from .records import Collection, Diagnostic, Module
from .slots import Slot

SOURCE_CACHE_SCHEMA = "paradev.source-family-cache.v2"
SOURCE_INVENTORY_SCHEMA = "paradev.source-family-inventory.v1"
_MAX_CACHE_BYTES = 64 * 1024 * 1024
_MAX_CACHE_JSON_BYTES = 512 * 1024 * 1024
_MAX_SOURCE_INVENTORY_ROWS = 250_000
_CACHE_CODE_PATHS = (
    Path(__file__),
    Path(__file__).with_name("discovery.py"),
    Path(__file__).with_name("loaders.py"),
    Path(__file__).with_name("slots.py"),
    Path(__file__).parent.parent / "pdx" / "ast.py",
    Path(__file__).parent.parent / "pdx" / "parser.py",
    Path(__file__).parent.parent / "pdx" / "token.py",
)
_CACHE_CODE_OBJECTS = (
    dmerge,
    load_txt,
    sha256hash,
    canonical_language,
)

_ResultT = TypeVar("_ResultT")
CacheStatus = Literal["hit", "miss", "refresh", "bypass"]
logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CachedSourceFamily:
    """One parsed family result and its cache disposition."""

    result: object
    status: CacheStatus
    record_count: int = 0
    signature: str | None = None


@dataclass(frozen=True, slots=True)
class _SourceFileToken:
    """Filesystem identity and change metadata for one source path."""

    size: int
    mtime_ns: int
    ctime_ns: int
    device: int
    inode: int


@dataclass(frozen=True, slots=True)
class _SourceInventoryEntry:
    """One content digest with the metadata that may safely reuse it."""

    relative_path: str
    sha256: str
    token: _SourceFileToken
    link_token: _SourceFileToken | None
    observed_before_ns: int
    observed_after_ns: int


@dataclass(frozen=True, slots=True)
class _FamilyFingerprint:
    """Complete content identity and reusable per-file observations."""

    digest: str
    snapshot: str
    entries: tuple[_SourceInventoryEntry, ...]
    cacheable: bool = True


class _SourceFingerprintDrift(RuntimeError):
    """One source changed while its fingerprint was being observed."""


class _SourceCacheBypass(RuntimeError):
    """One family topology cannot safely use parsed derived state."""


def cached_module_family(
    cache_root: Path,
    *,
    source_root: Path,
    family_root: Path,
    slots: Sequence[Slot],
    metadata_keys: Sequence[str],
    strict_metadata: bool,
    read: bool,
    write: bool,
    loader: Callable[[], object],
) -> CachedSourceFamily:
    """Load or rebuild one source-root module family cache entry."""

    return _cached_family(
        cache_root,
        kind="modules",
        source_root=source_root,
        family_root=family_root,
        slots=slots,
        metadata_keys=metadata_keys,
        strict_metadata=strict_metadata,
        read=read,
        write=write,
        loader=loader,
        encode=_encode_module_result,
        decode=_decode_module_result,
        record_count=lambda result: len(cast(Any, result).modules),
    )


def cached_collection_family(
    cache_root: Path,
    *,
    source_root: Path,
    family_root: Path,
    slots: Sequence[Slot],
    metadata_keys: Sequence[str],
    strict_metadata: bool,
    read: bool,
    write: bool,
    loader: Callable[[], object],
) -> CachedSourceFamily:
    """Load or rebuild one source-root collection family cache entry."""

    return _cached_family(
        cache_root,
        kind="collections",
        source_root=source_root,
        family_root=family_root,
        slots=slots,
        metadata_keys=metadata_keys,
        strict_metadata=strict_metadata,
        read=read,
        write=write,
        loader=loader,
        encode=_encode_collection_result,
        decode=_decode_collection_result,
        record_count=lambda result: len(cast(Any, result).collections),
    )


def _cached_family(
    cache_root: Path,
    *,
    kind: Literal["modules", "collections"],
    source_root: Path,
    family_root: Path,
    slots: Sequence[Slot],
    metadata_keys: Sequence[str],
    strict_metadata: bool,
    read: bool,
    write: bool,
    loader: Callable[[], _ResultT],
    encode: Callable[[_ResultT], dict[str, object]],
    decode: Callable[[Mapping[str, object]], _ResultT],
    record_count: Callable[[_ResultT], int],
) -> CachedSourceFamily:
    identity = _cache_identity(
        kind=kind,
        source_root=source_root,
        family_root=family_root,
    )
    path = _cache_path(cache_root, kind=kind, identity=identity)
    status: CacheStatus = "bypass" if not read else "miss"
    cache_exists = read and path.exists()
    document = _read_cache(path) if read else None
    previous_inventory: tuple[_SourceInventoryEntry, ...] = ()
    valid_document = False
    if document is not None:
        if document.get("schema") == SOURCE_CACHE_SCHEMA:
            try:
                previous_inventory = _decode_source_inventory(document.get("source_inventory"))
            except (KeyError, TypeError, ValueError) as error:
                logger.warning(
                    "Ignoring invalid source inventory in %s; the family will be reparsed (%s: %s).",
                    path,
                    type(error).__name__,
                    error,
                )
                status = "refresh"
            else:
                valid_document = True
        else:
            status = "refresh"
    elif cache_exists:
        status = "refresh"

    signature_base = {
        "engine": _cache_engine_fingerprint(),
        "identity": identity,
        "slots": [_slot_payload(slot) for slot in slots],
        "metadata_keys": sorted({str(key) for key in metadata_keys}),
        "strict_metadata": strict_metadata,
    }
    source_fingerprint: _FamilyFingerprint | None = None
    if valid_document and document is not None:
        cached_signature = _matching_source_cache_signature(
            document,
            expected_base=signature_base,
        )
        if cached_signature is not None:
            payload = document.get("payload")
            if isinstance(payload, Mapping):
                try:
                    result = decode(cast(Mapping[str, object], payload))
                except Exception as error:
                    logger.warning(
                        "Ignoring invalid parsed source cache %s; the family will be reparsed (%s: %s).",
                        path,
                        type(error).__name__,
                        error,
                    )
                    status = "refresh"
                else:
                    verified = _family_fingerprint(
                        family_root,
                        previous=previous_inventory,
                    )
                    if not verified.cacheable:
                        result = loader()
                        return CachedSourceFamily(
                            result=result,
                            status="bypass",
                            record_count=record_count(result),
                        )
                    if verified.digest == cached_signature["source"]:
                        if write and verified.entries != previous_inventory:
                            _write_cache_observably(
                                path,
                                signature=cached_signature,
                                source_inventory=verified.entries,
                                payload=cast(Mapping[str, object], payload),
                            )
                        return CachedSourceFamily(
                            result=result,
                            status="hit",
                            record_count=record_count(result),
                            signature=_signature_digest(cached_signature),
                        )
                    source_fingerprint = verified
                    status = "refresh"
            else:
                status = "refresh"
        else:
            status = "refresh"

    if source_fingerprint is None:
        source_fingerprint = _family_fingerprint(
            family_root,
            previous=previous_inventory if valid_document else (),
        )
    if not source_fingerprint.cacheable:
        result = loader()
        return CachedSourceFamily(
            result=result,
            status="bypass",
            record_count=record_count(result),
        )
    signature = {
        **signature_base,
        "source": source_fingerprint.digest,
    }
    signature_digest = _signature_digest(signature)
    before = source_fingerprint
    result = loader()
    after = _family_fingerprint(family_root, previous=before.entries)
    if not after.cacheable:
        result = loader()
        return CachedSourceFamily(
            result=result,
            status="bypass",
            record_count=record_count(result),
        )
    if not _same_family_snapshot(after, before):
        before = after
        result = loader()
        after = _family_fingerprint(family_root, previous=before.entries)
        if not after.cacheable:
            raise RuntimeError(
                f"Source family changed repeatedly during discovery: {family_root}. " "Wait for the external edit to finish and retry the build."
            )
        if not _same_family_snapshot(after, before):
            raise RuntimeError(
                f"Source family changed repeatedly during discovery: {family_root}. " "Wait for the external edit to finish and retry the build."
            )
        signature["source"] = after.digest
        signature_digest = _signature_digest(signature)
    if write:
        _write_cache_observably(
            path,
            signature=signature,
            source_inventory=after.entries,
            payload_factory=lambda: encode(result),
        )
    return CachedSourceFamily(
        result=result,
        status=status,
        record_count=record_count(result),
        signature=signature_digest,
    )


def _signature_digest(signature: Mapping[str, object]) -> str:
    """Return one deterministic cache-signature digest."""

    return hashlib.sha256(
        json.dumps(
            signature,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _same_family_snapshot(
    left: _FamilyFingerprint,
    right: _FamilyFingerprint,
) -> bool:
    """Return whether two fingerprints observed one stable source snapshot."""

    return left.digest == right.digest and left.snapshot == right.snapshot


def _matching_source_cache_signature(
    document: Mapping[str, object],
    *,
    expected_base: Mapping[str, object],
) -> dict[str, object] | None:
    value = document.get("signature")
    if not isinstance(value, Mapping):
        return None
    if set(value) != {*expected_base, "source"}:
        return None
    if any(value.get(key) != expected for key, expected in expected_base.items()):
        return None
    try:
        source = _sha256_text(value.get("source"), "signature.source")
    except (TypeError, ValueError):
        return None
    return {
        **expected_base,
        "source": source,
    }


def _cache_identity(
    *,
    kind: str,
    source_root: Path,
    family_root: Path,
) -> dict[str, str]:
    return {
        "kind": kind,
        "source_root": str(source_root.resolve()),
        "family_root": str(family_root.resolve()),
        "family": family_root.name,
    }


def _cache_path(
    cache_root: Path,
    *,
    kind: str,
    identity: Mapping[str, str],
) -> Path:
    key = hashlib.sha256(
        json.dumps(
            dict(identity),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return cache_root / kind / f"{key}.json.gz"


def _family_fingerprint(
    family_root: Path,
    *,
    previous: Sequence[_SourceInventoryEntry] = (),
) -> _FamilyFingerprint:
    """Return a stable family fingerprint, retrying one concurrent drift."""

    try:
        return _scan_family_fingerprint(
            family_root,
            previous=previous,
        )
    except _SourceCacheBypass:
        return _FamilyFingerprint(
            digest="",
            snapshot="",
            entries=(),
            cacheable=False,
        )
    except _SourceFingerprintDrift:
        try:
            return _scan_family_fingerprint(
                family_root,
                previous=(),
            )
        except _SourceCacheBypass:
            return _FamilyFingerprint(
                digest="",
                snapshot="",
                entries=(),
                cacheable=False,
            )
        except _SourceFingerprintDrift as error:
            raise RuntimeError(
                f"Source family changed repeatedly during fingerprint validation: {family_root}. " "Wait for the external edit to finish and retry the build."
            ) from error


def _scan_family_fingerprint(
    family_root: Path,
    *,
    previous: Sequence[_SourceInventoryEntry],
) -> _FamilyFingerprint:
    digest = hashlib.sha256()
    entries: list[_SourceInventoryEntry] = []
    previous_by_path = {entry.relative_path: entry for entry in previous}
    root_device, directories, source_paths = _family_source_paths(family_root)
    trusted_filesystem = _trusted_local_filesystem(
        family_root,
        device=root_device,
    )
    for relative_path, _token in directories:
        if relative_path == ".":
            continue
        relative = relative_path.encode("utf-8")
        digest.update(b"D")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
    for relative_path, path, listed_token in source_paths:
        observed_before_ns = time.time_ns()
        token, link_token = _source_file_tokens(path)
        if link_token is not None or token.device != root_device:
            raise _SourceCacheBypass(str(path))
        if token != listed_token:
            raise _SourceFingerprintDrift(str(path))
        previous_entry = previous_by_path.get(relative_path)
        reused_digest = previous_entry is not None and _can_reuse_source_digest(
            previous_entry,
            token=token,
            link_token=link_token,
            observed_before_ns=observed_before_ns,
            trusted_filesystem=trusted_filesystem,
        )
        if reused_digest and previous_entry is not None:
            sha256 = previous_entry.sha256
        else:
            sha256 = _hash_source_file(
                path,
                expected_token=token,
                expected_link_token=link_token,
            )
        observed_after_ns = time.time_ns()
        if reused_digest and previous_entry is not None:
            entry = previous_entry
        else:
            entry = _SourceInventoryEntry(
                relative_path=relative_path,
                sha256=sha256,
                token=token,
                link_token=link_token,
                observed_before_ns=observed_before_ns,
                observed_after_ns=observed_after_ns,
            )
        entries.append(entry)
        relative = relative_path.encode("utf-8")
        digest.update(b"F")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(sha256))
    entries_tuple = tuple(entries)
    _validate_family_snapshot(
        family_root,
        directories,
        entries_tuple,
        root_device=root_device,
    )
    return _FamilyFingerprint(
        digest=digest.hexdigest(),
        snapshot=_family_snapshot_digest(directories, entries_tuple),
        entries=entries_tuple,
    )


def _family_source_paths(
    family_root: Path,
) -> tuple[
    int,
    tuple[tuple[str, _SourceFileToken], ...],
    tuple[tuple[str, Path, _SourceFileToken], ...],
]:
    try:
        root_link_stat = family_root.lstat()
        root_stat = family_root.stat()
    except FileNotFoundError as error:
        raise _SourceFingerprintDrift(str(family_root)) from error
    if stat_module.S_ISLNK(root_link_stat.st_mode):
        raise _SourceCacheBypass(str(family_root))
    if not stat_module.S_ISDIR(root_stat.st_mode):
        raise _SourceFingerprintDrift(str(family_root))
    root_token = _source_file_token(root_link_stat)
    if _source_file_token(root_stat) != root_token:
        raise _SourceFingerprintDrift(str(family_root))
    root_device = int(root_stat.st_dev)
    directories_seen: list[tuple[str, _SourceFileToken]] = []
    source_paths: list[tuple[str, Path, _SourceFileToken]] = []
    pending = [(family_root, root_token)]
    while pending:
        directory_path, expected_token = pending.pop()
        token_before = _source_directory_token(
            directory_path,
            root_device=root_device,
        )
        if token_before != expected_token:
            raise _SourceFingerprintDrift(str(directory_path))
        try:
            with os.scandir(directory_path) as iterator:
                children = sorted(iterator, key=lambda item: item.name)
        except (FileNotFoundError, NotADirectoryError) as error:
            raise _SourceFingerprintDrift(str(directory_path)) from error
        child_directories: list[tuple[Path, _SourceFileToken]] = []
        for child in children:
            path = directory_path / child.name
            try:
                link_stat = child.stat(follow_symlinks=False)
            except FileNotFoundError as error:
                raise _SourceFingerprintDrift(str(path)) from error
            if stat_module.S_ISLNK(link_stat.st_mode):
                raise _SourceCacheBypass(str(path))
            if int(link_stat.st_dev) != root_device:
                raise _SourceCacheBypass(str(path))
            token = _source_file_token(link_stat)
            if stat_module.S_ISDIR(link_stat.st_mode):
                child_directories.append((path, token))
            elif stat_module.S_ISREG(link_stat.st_mode):
                source_paths.append(
                    (
                        path.relative_to(family_root).as_posix(),
                        path,
                        token,
                    )
                )
        token_after = _source_directory_token(
            directory_path,
            root_device=root_device,
        )
        if token_after != token_before:
            raise _SourceFingerprintDrift(str(directory_path))
        directories_seen.append(
            (
                directory_path.relative_to(family_root).as_posix(),
                token_after,
            )
        )
        pending.extend(reversed(child_directories))
    return (
        root_device,
        tuple(sorted(directories_seen, key=lambda item: item[0])),
        tuple(sorted(source_paths, key=lambda item: item[0])),
    )


def _validate_family_snapshot(
    family_root: Path,
    directories: Sequence[tuple[str, _SourceFileToken]],
    entries: Sequence[_SourceInventoryEntry],
    *,
    root_device: int,
) -> None:
    for entry in entries:
        path = family_root / entry.relative_path
        token, link_token = _source_file_tokens(path)
        if link_token is not None or token.device != root_device:
            raise _SourceCacheBypass(str(path))
        if token != entry.token or link_token != entry.link_token:
            raise _SourceFingerprintDrift(str(path))
    for relative_path, expected_token in directories:
        path = family_root if relative_path == "." else family_root / relative_path
        token = _source_directory_token(
            path,
            root_device=root_device,
        )
        if token != expected_token:
            raise _SourceFingerprintDrift(str(path))


def _family_snapshot_digest(
    directories: Sequence[tuple[str, _SourceFileToken]],
    entries: Sequence[_SourceInventoryEntry],
) -> str:
    """Return one metadata-sensitive token for discovery race detection."""

    digest = hashlib.sha256()
    for relative_path, token in directories:
        _update_snapshot_digest(digest, b"D", relative_path, token)
    for entry in entries:
        _update_snapshot_digest(
            digest,
            b"F",
            entry.relative_path,
            entry.token,
            sha256=entry.sha256,
        )
    return digest.hexdigest()


def _update_snapshot_digest(
    digest: Any,
    kind: bytes,
    relative_path: str,
    token: _SourceFileToken,
    *,
    sha256: str | None = None,
) -> None:
    digest.update(kind)
    values = (
        relative_path,
        str(token.size),
        str(token.mtime_ns),
        str(token.ctime_ns),
        str(token.device),
        str(token.inode),
        sha256 or "",
    )
    for value in values:
        encoded = value.encode("utf-8")
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)


def _source_directory_token(
    path: Path,
    *,
    root_device: int,
) -> _SourceFileToken:
    try:
        link_stat = path.lstat()
    except FileNotFoundError as error:
        raise _SourceFingerprintDrift(str(path)) from error
    if stat_module.S_ISLNK(link_stat.st_mode):
        raise _SourceCacheBypass(str(path))
    if not stat_module.S_ISDIR(link_stat.st_mode):
        raise _SourceFingerprintDrift(str(path))
    if int(link_stat.st_dev) != root_device:
        raise _SourceCacheBypass(str(path))
    return _source_file_token(link_stat)


def _source_file_tokens(
    path: Path,
) -> tuple[_SourceFileToken, _SourceFileToken | None]:
    try:
        link_stat = path.lstat()
    except FileNotFoundError as error:
        raise _SourceFingerprintDrift(str(path)) from error
    if stat_module.S_ISLNK(link_stat.st_mode):
        try:
            target_stat = path.stat()
        except FileNotFoundError as error:
            raise _SourceFingerprintDrift(str(path)) from error
        if not stat_module.S_ISREG(target_stat.st_mode):
            raise _SourceFingerprintDrift(str(path))
        return _source_file_token(target_stat), _source_file_token(link_stat)
    if not stat_module.S_ISREG(link_stat.st_mode):
        raise _SourceFingerprintDrift(str(path))
    return _source_file_token(link_stat), None


def _source_file_token(value: os.stat_result) -> _SourceFileToken:
    return _SourceFileToken(
        size=int(value.st_size),
        mtime_ns=int(value.st_mtime_ns),
        ctime_ns=int(value.st_ctime_ns),
        device=int(value.st_dev),
        inode=int(value.st_ino),
    )


def _can_reuse_source_digest(
    previous: _SourceInventoryEntry,
    *,
    token: _SourceFileToken,
    link_token: _SourceFileToken | None,
    observed_before_ns: int,
    trusted_filesystem: bool,
) -> bool:
    if not trusted_filesystem:
        return False
    if previous.token != token or previous.link_token != link_token:
        return False
    if not _source_metadata_is_reliable(
        previous.token,
        observed_before_ns=previous.observed_before_ns,
    ):
        return False
    if previous.link_token is not None and not _source_metadata_is_reliable(
        previous.link_token,
        observed_before_ns=previous.observed_before_ns,
    ):
        return False
    if not _source_metadata_is_reliable(
        token,
        observed_before_ns=observed_before_ns,
    ):
        return False
    if link_token is not None and not _source_metadata_is_reliable(
        link_token,
        observed_before_ns=observed_before_ns,
    ):
        return False
    return previous.observed_after_ns >= previous.observed_before_ns


def _source_metadata_is_reliable(
    token: _SourceFileToken,
    *,
    observed_before_ns: int,
) -> bool:
    if token.size < 0 or token.device <= 0 or token.inode <= 0:
        return False
    if token.mtime_ns <= 0 or token.ctime_ns <= 0:
        return False
    if max(token.mtime_ns, token.ctime_ns) >= observed_before_ns:
        return False
    return token.ctime_ns % 1_000_000_000 != 0


def _hash_source_file(
    path: Path,
    *,
    expected_token: _SourceFileToken,
    expected_link_token: _SourceFileToken | None,
) -> str:
    if expected_link_token is not None:
        raise _SourceCacheBypass(str(path))
    flags = os.O_RDONLY
    flags |= getattr(os, "O_CLOEXEC", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as error:
        raise _SourceFingerprintDrift(str(path)) from error
    except OSError as error:
        try:
            link_stat = path.lstat()
        except FileNotFoundError as missing_error:
            raise _SourceFingerprintDrift(str(path)) from missing_error
        if stat_module.S_ISLNK(link_stat.st_mode):
            raise _SourceCacheBypass(str(path)) from error
        raise
    digest = hashlib.sha256()
    try:
        opened_before = os.fstat(descriptor)
        opened_token = _source_file_token(opened_before)
        if not stat_module.S_ISREG(opened_before.st_mode) or opened_token != expected_token:
            raise _SourceFingerprintDrift(str(path))
        while chunk := os.read(descriptor, 1024 * 1024):
            digest.update(chunk)
        opened_after = os.fstat(descriptor)
        if _source_file_token(opened_after) != opened_token:
            raise _SourceFingerprintDrift(str(path))
    finally:
        os.close(descriptor)
    token_after, link_token_after = _source_file_tokens(path)
    if token_after != expected_token or link_token_after != expected_link_token:
        raise _SourceFingerprintDrift(str(path))
    return digest.hexdigest()


_TRUSTED_LOCAL_FILESYSTEMS = frozenset(
    {
        "apfs",
        "hfs",
        "hfsplus",
        "ext2",
        "ext3",
        "ext4",
        "xfs",
        "btrfs",
        "zfs",
        "tmpfs",
        "ramfs",
    }
)


def _trusted_local_filesystem(path: Path, *, device: int) -> bool:
    if os.name != "posix":
        return False
    filesystem = _filesystem_kind(path, device)
    return filesystem in _TRUSTED_LOCAL_FILESYSTEMS


def _filesystem_kind(path: Path, device: int) -> str:
    del path
    return _filesystem_kind_for_device(device)


@lru_cache(maxsize=64)
def _filesystem_kind_for_device(device: int) -> str:
    return _probe_filesystem_kind(device)


def _probe_filesystem_kind(device: int) -> str:
    if sys.platform == "darwin":
        for mount_device, filesystem, local in _macos_mount_table():
            if mount_device == device:
                return filesystem if local else ""
        return ""
    if sys.platform.startswith("linux"):
        identity = f"{os.major(device)}:{os.minor(device)}"
        return _linux_filesystems_by_device().get(identity, "")
    return ""


@lru_cache(maxsize=1)
def _macos_mount_table() -> tuple[tuple[int, str, bool], ...]:
    try:
        completed = cmd(
            ["/sbin/mount"],
            shell=False,
            include=("code", "out"),
        )
    except OSError:
        return ()
    if not isinstance(completed, Mapping) or completed.get("code") != 0:
        return ()
    output = completed.get("out")
    if not isinstance(output, str):
        return ()
    rows: list[tuple[int, str, bool]] = []
    for line in output.splitlines():
        _source, separator, mounted = line.partition(" on ")
        if not separator:
            continue
        mount_text, separator, details = mounted.rpartition(" (")
        if not separator or not details.endswith(")"):
            continue
        detail_parts = [part.strip().lower() for part in details[:-1].split(",")]
        if not mount_text or not detail_parts:
            continue
        try:
            mount_device = int(Path(mount_text).stat().st_dev)
        except OSError:
            continue
        rows.append(
            (
                mount_device,
                detail_parts[0],
                "local" in detail_parts[1:],
            )
        )
    return tuple(rows)


@lru_cache(maxsize=1)
def _linux_filesystems_by_device() -> dict[str, str]:
    try:
        lines = Path("/proc/self/mountinfo").read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    filesystems: dict[str, str] = {}
    for line in lines:
        before, separator, after = line.partition(" - ")
        before_parts = before.split()
        after_parts = after.split()
        if not separator or len(before_parts) < 3 or not after_parts:
            continue
        identity = before_parts[2]
        filesystem = after_parts[0].lower()
        current = filesystems.get(identity)
        if current is None or current == filesystem:
            filesystems[identity] = filesystem
        else:
            filesystems[identity] = ""
    return filesystems


def _write_cache_observably(
    path: Path,
    *,
    signature: Mapping[str, object],
    source_inventory: Sequence[_SourceInventoryEntry],
    payload: Mapping[str, object] | None = None,
    payload_factory: Callable[[], Mapping[str, object]] | None = None,
) -> None:
    try:
        if payload is None:
            if payload_factory is None:
                raise TypeError("Parsed source cache payload is required.")
            payload = payload_factory()
        _write_cache(
            path,
            {
                "schema": SOURCE_CACHE_SCHEMA,
                "signature": dict(signature),
                "source_inventory": _encode_source_inventory(source_inventory),
                "payload": dict(payload),
            },
        )
    except Exception as error:
        logger.warning(
            "Could not write parsed source cache %s; this build remains valid but later builds may reparse the family (%s: %s).",
            path,
            type(error).__name__,
            error,
        )


def _encode_source_inventory(
    entries: Sequence[_SourceInventoryEntry],
) -> dict[str, object]:
    if len(entries) > _MAX_SOURCE_INVENTORY_ROWS:
        raise ValueError("Source inventory exceeds the safe row limit.")
    rows = [_encode_source_inventory_entry(entry) for entry in entries]
    return {
        "schema": SOURCE_INVENTORY_SCHEMA,
        "entries": rows,
        "checksum": _source_inventory_checksum(rows),
    }


def _decode_source_inventory(
    value: object,
) -> tuple[_SourceInventoryEntry, ...]:
    inventory = _mapping(value, "source_inventory")
    _require_exact_keys(
        inventory,
        {"schema", "entries", "checksum"},
        "source_inventory",
    )
    if inventory.get("schema") != SOURCE_INVENTORY_SCHEMA:
        raise ValueError("Source inventory schema is unsupported.")
    rows_value = inventory.get("entries")
    if not isinstance(rows_value, Sequence) or isinstance(rows_value, (str, bytes)):
        raise TypeError("source_inventory.entries must be a sequence.")
    if len(rows_value) > _MAX_SOURCE_INVENTORY_ROWS:
        raise ValueError("Source inventory exceeds the safe row limit.")
    rows = [_mapping(row, f"source_inventory.entries[{index}]") for index, row in enumerate(rows_value)]
    checksum = _sha256_text(
        inventory.get("checksum"),
        "source_inventory.checksum",
    )
    if checksum != _source_inventory_checksum(rows):
        raise ValueError("Source inventory checksum does not match its entries.")
    entries = tuple(_decode_source_inventory_entry(row, index=index) for index, row in enumerate(rows))
    paths = [entry.relative_path for entry in entries]
    if paths != sorted(paths) or len(paths) != len(set(paths)):
        raise ValueError("Source inventory paths must be unique and strictly sorted.")
    return entries


def _encode_source_inventory_entry(
    entry: _SourceInventoryEntry,
) -> dict[str, object]:
    return {
        "path": entry.relative_path,
        "sha256": entry.sha256,
        "token": _encode_source_file_token(entry.token),
        "link_token": (_encode_source_file_token(entry.link_token) if entry.link_token is not None else None),
        "observed_before_ns": entry.observed_before_ns,
        "observed_after_ns": entry.observed_after_ns,
    }


def _decode_source_inventory_entry(
    value: Mapping[str, object],
    *,
    index: int,
) -> _SourceInventoryEntry:
    name = f"source_inventory.entries[{index}]"
    _require_exact_keys(
        value,
        {
            "path",
            "sha256",
            "token",
            "link_token",
            "observed_before_ns",
            "observed_after_ns",
        },
        name,
    )
    relative_path = _text(value.get("path"), f"{name}.path")
    if relative_path.startswith("/") or "\\" in relative_path or any(part in {"", ".", ".."} for part in relative_path.split("/")):
        raise ValueError(f"{name}.path must be a safe relative POSIX path.")
    observed_before_ns = _nonnegative_integer(
        value.get("observed_before_ns"),
        f"{name}.observed_before_ns",
    )
    observed_after_ns = _nonnegative_integer(
        value.get("observed_after_ns"),
        f"{name}.observed_after_ns",
    )
    if observed_after_ns < observed_before_ns:
        raise ValueError(f"{name} has an invalid observation interval.")
    link_value = value.get("link_token")
    return _SourceInventoryEntry(
        relative_path=relative_path,
        sha256=_sha256_text(value.get("sha256"), f"{name}.sha256"),
        token=_decode_source_file_token(value.get("token"), f"{name}.token"),
        link_token=(None if link_value is None else _decode_source_file_token(link_value, f"{name}.link_token")),
        observed_before_ns=observed_before_ns,
        observed_after_ns=observed_after_ns,
    )


def _encode_source_file_token(token: _SourceFileToken) -> dict[str, int]:
    return {
        "size": token.size,
        "mtime_ns": token.mtime_ns,
        "ctime_ns": token.ctime_ns,
        "device": token.device,
        "inode": token.inode,
    }


def _decode_source_file_token(value: object, name: str) -> _SourceFileToken:
    token = _mapping(value, name)
    _require_exact_keys(
        token,
        {"size", "mtime_ns", "ctime_ns", "device", "inode"},
        name,
    )
    return _SourceFileToken(
        size=_nonnegative_integer(token.get("size"), f"{name}.size"),
        mtime_ns=_nonnegative_integer(
            token.get("mtime_ns"),
            f"{name}.mtime_ns",
        ),
        ctime_ns=_nonnegative_integer(
            token.get("ctime_ns"),
            f"{name}.ctime_ns",
        ),
        device=_nonnegative_integer(token.get("device"), f"{name}.device"),
        inode=_nonnegative_integer(token.get("inode"), f"{name}.inode"),
    )


def _source_inventory_checksum(
    rows: Sequence[Mapping[str, object]],
) -> str:
    payload = {
        "schema": SOURCE_INVENTORY_SCHEMA,
        "entries": list(rows),
    }
    return hashlib.sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _require_exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    name: str,
) -> None:
    actual = set(value)
    if actual != expected:
        raise ValueError(f"{name} keys do not match the source inventory contract.")


def _sha256_text(value: object, name: str) -> str:
    text = _text(value, name)
    if len(text) != 64 or text != text.lower() or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest.")
    return text


def _nonnegative_integer(value: object, name: str) -> int:
    integer = _integer(value, name)
    if integer < 0:
        raise ValueError(f"{name} must not be negative.")
    return integer


def _slot_payload(slot: Slot) -> dict[str, object]:
    return {
        "name": slot.name,
        "match": slot.match,
        "required": slot.required,
        "many": slot.many,
        "regex": slot.regex,
        "kind": slot.kind,
        "shared": slot.shared,
        "authoring_path": slot.authoring_path,
    }


@lru_cache(maxsize=1)
def _cache_engine_fingerprint() -> str:
    digest = hashlib.sha256()
    runtime = {
        "schema": SOURCE_CACHE_SCHEMA,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "paradev": _package_version("paradev"),
        "heavenbase": _package_version("heavenbase"),
        "pyyaml": _package_version("PyYAML"),
    }
    digest.update(json.dumps(runtime, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    code_paths = set(_CACHE_CODE_PATHS)
    code_paths.update(Path(source_path) for item in _CACHE_CODE_OBJECTS if (source_path := getsourcefile(item)) is not None)
    for path in sorted(code_paths, key=str):
        try:
            payload = path.read_bytes()
        except OSError:
            continue
        digest.update(str(path).encode("utf-8"))
        digest.update(hashlib.sha256(payload).digest())
    return digest.hexdigest()


def _package_version(package: str) -> str:
    try:
        return version(package)
    except PackageNotFoundError:
        return "uninstalled"


def _read_cache(path: Path) -> dict[str, object] | None:
    try:
        if path.stat().st_size > _MAX_CACHE_BYTES:
            return None
        compressed = path.read_bytes()
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as stream:
            payload = stream.read(_MAX_CACHE_JSON_BYTES + 1)
        if len(payload) > _MAX_CACHE_JSON_BYTES:
            return None
        document = json.loads(payload)
    except (EOFError, OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return document if isinstance(document, dict) else None


def _write_cache(path: Path, document: Mapping[str, object]) -> None:
    payload = json.dumps(
        document,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(payload) > _MAX_CACHE_JSON_BYTES:
        raise ValueError("Parsed source cache entry exceeds the safe JSON size limit.")
    compressed = gzip.compress(payload, compresslevel=1, mtime=0)
    if len(compressed) > _MAX_CACHE_BYTES:
        raise ValueError("Parsed source cache entry exceeds the safe file size limit.")
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(compressed)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def _encode_module_result(result: object) -> dict[str, object]:
    modules = cast(Any, result).modules
    diagnostics = cast(Any, result).diagnostics
    return {
        "modules": [_encode_module(module) for module in modules],
        "diagnostics": [_encode_diagnostic(item) for item in diagnostics],
    }


def _decode_module_result(payload: Mapping[str, object]) -> object:
    from .discovery import ModuleDiscoveryResult

    return ModuleDiscoveryResult(
        modules=tuple(_decode_module(item) for item in _mapping_sequence(payload.get("modules"), "modules")),
        diagnostics=tuple(
            _decode_diagnostic(item)
            for item in _mapping_sequence(
                payload.get("diagnostics"),
                "diagnostics",
            )
        ),
    )


def _encode_collection_result(result: object) -> dict[str, object]:
    collections = cast(Any, result).collections
    diagnostics = cast(Any, result).diagnostics
    return {
        "collections": [_encode_collection(item) for item in collections],
        "diagnostics": [_encode_diagnostic(item) for item in diagnostics],
    }


def _decode_collection_result(payload: Mapping[str, object]) -> object:
    from .discovery import CollectionDiscoveryResult

    return CollectionDiscoveryResult(
        collections=tuple(
            _decode_collection(item)
            for item in _mapping_sequence(
                payload.get("collections"),
                "collections",
            )
        ),
        diagnostics=tuple(
            _decode_diagnostic(item)
            for item in _mapping_sequence(
                payload.get("diagnostics"),
                "diagnostics",
            )
        ),
    )


def _encode_module(module: Module) -> dict[str, object]:
    if not isinstance(module.payload, ModuleSourceBundle):
        raise TypeError("Discovered module payload is not cacheable.")
    return {
        "module_id": module.module_id,
        "family": module.family,
        "root": str(module.root),
        "source_slots": _encode_source_slots(module.source_slots),
        "collection_id": module.collection_id,
        "metadata": dict(module.metadata),
        "payload": _encode_module_bundle(module.payload),
    }


def _decode_module(payload: Mapping[str, object]) -> Module:
    bundle = _decode_module_bundle(_mapping(payload.get("payload"), "payload"))
    family = _text(payload.get("family"), "family")
    if bundle.metadata.get("type") != family:
        raise ValueError("Cached module family disagrees with its parsed metadata.")
    module = bundle.to_module(family=family)
    expected = {
        "module_id": module.module_id,
        "root": str(module.root),
        "source_slots": _encode_source_slots(module.source_slots),
        "collection_id": module.collection_id,
        "metadata": dict(module.metadata),
    }
    actual = {
        "module_id": _text(payload.get("module_id"), "module_id"),
        "root": _text(payload.get("root"), "root"),
        "source_slots": _encode_source_slots(_decode_source_slots(payload.get("source_slots"))),
        "collection_id": _optional_text(
            payload.get("collection_id"),
            "collection_id",
        ),
        "metadata": dict(_mapping(payload.get("metadata"), "metadata")),
    }
    if actual != expected:
        raise ValueError(f"Cached module {module.module_id!r} disagrees with its parsed source bundle.")
    return module


def _encode_collection(collection: Collection) -> dict[str, object]:
    if not isinstance(collection.payload, CollectionSourceBundle):
        raise TypeError("Discovered collection payload is not cacheable.")
    return {
        "collection_id": collection.collection_id,
        "family": collection.family,
        "module_ids": list(collection.module_ids),
        "source_slots": _encode_source_slots(collection.source_slots),
        "metadata": dict(collection.metadata),
        "payload": _encode_collection_bundle(collection.payload),
    }


def _decode_collection(payload: Mapping[str, object]) -> Collection:
    bundle = _decode_collection_bundle(_mapping(payload.get("payload"), "payload"))
    family = _text(payload.get("family"), "family")
    collection_id = _text(payload.get("collection_id"), "collection_id")
    if bundle.family != family or bundle.collection_id != collection_id:
        raise ValueError("Cached collection identity disagrees with its parsed source bundle.")
    collection = bundle.to_collection()
    expected = {
        "module_ids": collection.module_ids,
        "source_slots": _encode_source_slots(collection.source_slots),
        "metadata": dict(collection.metadata),
    }
    actual = {
        "module_ids": _text_sequence(payload.get("module_ids"), "module_ids"),
        "source_slots": _encode_source_slots(_decode_source_slots(payload.get("source_slots"))),
        "metadata": dict(_mapping(payload.get("metadata"), "metadata")),
    }
    if actual != expected:
        raise ValueError(f"Cached collection {collection.collection_id!r} disagrees with its parsed source bundle.")
    return collection


def _encode_module_bundle(bundle: ModuleSourceBundle) -> dict[str, object]:
    return {
        "root": bundle.root,
        "source_slots": _encode_source_slots(bundle.source_slots),
        "metadata": dict(bundle.metadata),
        "pdx_sources": [_encode_pdx_source(item) for item in bundle.pdx_sources],
        "loc_entries": [_encode_loc_entry(item) for item in bundle.loc_entries],
        "copy_sources": [_encode_copy_source(item) for item in bundle.copy_sources],
        "diagnostics": [_encode_diagnostic(item) for item in bundle.diagnostics],
        "module_id": bundle.module_id,
    }


def _decode_module_bundle(payload: Mapping[str, object]) -> ModuleSourceBundle:
    return ModuleSourceBundle(
        root=_text(payload.get("root"), "root"),
        source_slots=_decode_source_slots(payload.get("source_slots")),
        metadata=dict(_mapping(payload.get("metadata"), "metadata")),
        pdx_sources=tuple(
            _decode_pdx_source(item)
            for item in _mapping_sequence(
                payload.get("pdx_sources"),
                "pdx_sources",
            )
        ),
        loc_entries=tuple(
            _decode_loc_entry(item)
            for item in _mapping_sequence(
                payload.get("loc_entries"),
                "loc_entries",
            )
        ),
        copy_sources=tuple(
            _decode_copy_source(item)
            for item in _mapping_sequence(
                payload.get("copy_sources"),
                "copy_sources",
            )
        ),
        diagnostics=tuple(
            _decode_diagnostic(item)
            for item in _mapping_sequence(
                payload.get("diagnostics"),
                "diagnostics",
            )
        ),
        module_id=_optional_text(payload.get("module_id"), "module_id"),
    )


def _encode_collection_bundle(bundle: CollectionSourceBundle) -> dict[str, object]:
    return {
        "root": bundle.root,
        "metadata": dict(bundle.metadata),
        "source_slots": _encode_source_slots(bundle.source_slots),
        "pdx_sources": [_encode_pdx_source(item) for item in bundle.pdx_sources],
        "loc_entries": [_encode_loc_entry(item) for item in bundle.loc_entries],
        "copy_sources": [_encode_copy_source(item) for item in bundle.copy_sources],
        "diagnostics": [_encode_diagnostic(item) for item in bundle.diagnostics],
        "collection_id": bundle.collection_id,
        "family": bundle.family,
    }


def _decode_collection_bundle(
    payload: Mapping[str, object],
) -> CollectionSourceBundle:
    return CollectionSourceBundle(
        root=_text(payload.get("root"), "root"),
        metadata=dict(_mapping(payload.get("metadata"), "metadata")),
        source_slots=_decode_source_slots(payload.get("source_slots")),
        pdx_sources=tuple(
            _decode_pdx_source(item)
            for item in _mapping_sequence(
                payload.get("pdx_sources"),
                "pdx_sources",
            )
        ),
        loc_entries=tuple(
            _decode_loc_entry(item)
            for item in _mapping_sequence(
                payload.get("loc_entries"),
                "loc_entries",
            )
        ),
        copy_sources=tuple(
            _decode_copy_source(item)
            for item in _mapping_sequence(
                payload.get("copy_sources"),
                "copy_sources",
            )
        ),
        diagnostics=tuple(
            _decode_diagnostic(item)
            for item in _mapping_sequence(
                payload.get("diagnostics"),
                "diagnostics",
            )
        ),
        collection_id=_optional_text(
            payload.get("collection_id"),
            "collection_id",
        ),
        family=_optional_text(payload.get("family"), "family"),
    )


def _encode_pdx_source(source: PDXBlockSource) -> dict[str, object]:
    return {
        "slot": source.slot,
        "path": source.path,
        "block": source.block.dump(),
    }


def _decode_pdx_source(payload: Mapping[str, object]) -> PDXBlockSource:
    return PDXBlockSource(
        slot=_text(payload.get("slot"), "slot"),
        path=_text(payload.get("path"), "path"),
        block=PDXBlock.load(_mapping(payload.get("block"), "block")),
    )


def _encode_loc_entry(entry: LocalizationEntry) -> dict[str, object]:
    return {
        "key": entry.key,
        "language": entry.language,
        "text": entry.text,
        "source_path": entry.source_path,
        "module_id": entry.module_id,
    }


def _decode_loc_entry(payload: Mapping[str, object]) -> LocalizationEntry:
    return LocalizationEntry(
        key=_text(payload.get("key"), "key"),
        language=_text(payload.get("language"), "language"),
        text=_text(payload.get("text"), "text", allow_empty=True),
        source_path=_text(payload.get("source_path"), "source_path"),
        module_id=_optional_text(payload.get("module_id"), "module_id"),
    )


def _encode_copy_source(source: CopySource) -> dict[str, object]:
    return {
        "slot": source.slot,
        "path": source.path,
        "output_path": source.output_path,
        "sha256": source.sha256,
        "content_sha256": source.content_sha256,
        "size": source.size,
        "media_type": source.media_type,
        "format": source.format,
        "width": source.width,
        "height": source.height,
    }


def _decode_copy_source(payload: Mapping[str, object]) -> CopySource:
    return CopySource(
        slot=_text(payload.get("slot"), "slot"),
        path=_text(payload.get("path"), "path"),
        output_path=_text(payload.get("output_path"), "output_path"),
        sha256=_text(payload.get("sha256"), "sha256"),
        size=_integer(payload.get("size"), "size"),
        content_sha256=_optional_text(
            payload.get("content_sha256"),
            "content_sha256",
        ),
        media_type=_optional_text(payload.get("media_type"), "media_type"),
        format=_optional_text(payload.get("format"), "format"),
        width=_optional_integer(payload.get("width"), "width"),
        height=_optional_integer(payload.get("height"), "height"),
    )


def _encode_diagnostic(diagnostic: Diagnostic) -> dict[str, object]:
    return diagnostic.to_dict()


def _decode_diagnostic(payload: Mapping[str, object]) -> Diagnostic:
    span_value = payload.get("span")
    span = None
    if span_value is not None:
        span = {str(key): _integer(value, f"span.{key}") for key, value in _mapping(span_value, "span").items()}
    return Diagnostic(
        code=_text(payload.get("code"), "code"),
        message=_text(payload.get("message"), "message", allow_empty=True),
        severity=_text(payload.get("severity"), "severity"),
        family=_optional_text(payload.get("family"), "family"),
        module_id=_optional_text(payload.get("module_id"), "module_id"),
        collection_id=_optional_text(
            payload.get("collection_id"),
            "collection_id",
        ),
        slot=_optional_text(payload.get("slot"), "slot"),
        source_path=_optional_text(payload.get("source_path"), "source_path"),
        artifact_path=_optional_text(
            payload.get("artifact_path"),
            "artifact_path",
        ),
        target_root=_optional_text(payload.get("target_root"), "target_root"),
        span=span,
        slots=_text_sequence(payload.get("slots", ()), "slots"),
        owners=_text_sequence(payload.get("owners", ()), "owners"),
    )


def _encode_source_slots(
    source_slots: Mapping[str, Sequence[str | Path]],
) -> dict[str, list[str]]:
    return {str(slot): [str(path) for path in paths] for slot, paths in sorted(source_slots.items())}


def _decode_source_slots(value: object) -> dict[str, tuple[str, ...]]:
    return {str(slot): _text_sequence(paths, f"source_slots.{slot}") for slot, paths in _mapping(value, "source_slots").items()}


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping.")
    return cast(Mapping[str, object], value)


def _mapping_sequence(
    value: object,
    name: str,
) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence.")
    return tuple(_mapping(item, f"{name}[]") for item in value)


def _text(value: object, name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value):
        raise TypeError(f"{name} must be a string.")
    return value


def _optional_text(value: object, name: str) -> str | None:
    if value is None:
        return None
    return _text(value, name)


def _text_sequence(value: object, name: str) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must be a sequence.")
    return tuple(_text(item, f"{name}[]") for item in value)


def _integer(value: object, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer.")
    return value


def _optional_integer(value: object, name: str) -> int | None:
    if value is None:
        return None
    return _integer(value, name)
