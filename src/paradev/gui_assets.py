"""Resolve ParaDev GUI assets across source and wheel installations."""

from __future__ import annotations

__all__ = ["gui_host_file", "gui_root"]

from importlib import resources
from importlib.metadata import PackageNotFoundError, distribution
import sysconfig

from heavenbase.utils import exists_file, get_file_dir, pj


def gui_root() -> str:
    """Return the packaged React application root."""

    return str(resources.files("paradev.resources").joinpath("gui"))


def gui_host_file(name: str) -> str:
    """Resolve one desktop-host asset from a checkout or installed wheel."""

    if not name or name.replace("\\", "/").rsplit("/", 1)[-1] != name:
        raise ValueError(f"GUI host asset must be a file name: {name!r}")

    relative = pj("share", "paradev", "gui", "host", name)
    repository = pj(get_file_dir(__file__), "..", "..", abs=True)
    source = pj(repository, "apps", "desktop", "host", name, abs=True)
    if exists_file(source):
        return source

    installed = pj(sysconfig.get_path("data"), relative, abs=True)
    if exists_file(installed):
        return installed

    try:
        package = distribution("paradev")
    except PackageNotFoundError:
        return installed
    suffix = relative.replace("\\", "/")
    for entry in package.files or ():
        if entry.as_posix().endswith(suffix):
            candidate = str(package.locate_file(entry))
            if exists_file(candidate):
                return candidate
    return installed
