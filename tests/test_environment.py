from pathlib import Path
import shlex
import sys

from heavenbase.utils import cmd, load_txt, pj, save_txt, touch_dir


def _readme_sync_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "readme-sync"
    touch_dir(root / "scripts")
    touch_dir(root / "src" / "paradev" / "resources")
    source = "# Example\n\n```bash\necho hello\n```"
    translation = "# 示例\n\n```bash\necho hello\n```"
    save_txt(load_txt("scripts/sync-readme.bash"), root / "scripts" / "sync-readme.bash")
    save_txt(f'run_python() {{ {shlex.quote(sys.executable)} "$@"; }}\n', root / "scripts" / "_env.bash")
    save_txt(source, root / "README.en.md")
    save_txt(translation, root / "README.zh.md")
    save_txt(source, root / "README.md")
    save_txt(source, root / "src" / "paradev" / "resources" / "README.md")
    return root


def test_readme_sync_accepts_aligned_bilingual_sources(tmp_path: Path) -> None:
    root = _readme_sync_fixture(tmp_path)

    output = cmd(
        ["bash", root / "scripts" / "sync-readme.bash", "--check"],
        check=True,
        cwd=root,
        include="out",
    )

    assert "[readme] bilingual pair aligned (5 lines, 1 code block(s))" in output
    assert "[readme] 2 target(s) current" in output


def test_readme_sync_rejects_translation_line_drift(tmp_path: Path) -> None:
    root = _readme_sync_fixture(tmp_path)
    save_txt("# 示例", root / "README.zh.md")

    result = cmd(
        ["bash", root / "scripts" / "sync-readme.bash", "--check"],
        cwd=root,
        include=["code", "err"],
    )

    assert result["code"] == 1
    assert "README.zh.md has 1 lines; expected 5" in result["err"]


def test_heavenbase_source_override_targets_repo_venv() -> None:
    sync_script = load_txt("scripts/sync-env.bash")

    assert 'python="$(venv_python "${ROOT}/.venv")"' in sync_script
    assert '"${UV_BIN}" pip install --python "${python}" --reinstall --no-deps -e "${source}"' in sync_script
    assert 'marker="$(heavenbase_override_marker)"' in sync_script


def test_heavenbase_source_discovery_uses_linked_worktree_checkout(
    tmp_path: Path,
) -> None:
    projects_root = tmp_path / "Projects"
    checkout_root = projects_root / "ParaDev"
    worktree_root = tmp_path / "linked-worktrees" / "feature"
    common_dir = checkout_root / ".git"
    source = projects_root / "HeavenBase" / "HeavenBase"
    fake_bin = tmp_path / "bin"
    touch_dir(source / "src" / "heavenbase")
    touch_dir(worktree_root)
    touch_dir(common_dir)
    touch_dir(fake_bin)
    save_txt("[project]\nname = 'heavenbase'\n", source / "pyproject.toml")
    fake_git = fake_bin / "git"
    save_txt(
        "#!/usr/bin/env bash\nprintf '%s\\n' \"${FAKE_GIT_COMMON_DIR}\"\n",
        fake_git,
    )
    cmd(["chmod", "+x", fake_git], check=True)

    output = cmd(
        [
            "bash",
            "-c",
            ('PATH="$1:$PATH"; export FAKE_GIT_COMMON_DIR="$2"; ' 'source "$3"; discover_local_heavenbase_source "$4"'),
            "test-worktree-heavenbase-source",
            str(fake_bin),
            str(common_dir),
            pj("scripts", "_env.bash", abs=True),
            str(worktree_root),
        ],
        check=True,
        include="out",
    )

    assert output == str(source)


def test_python_wrappers_preserve_active_heavenbase_source_override() -> None:
    env_script = load_txt("scripts/_env.bash")
    sync_script = load_txt("scripts/sync-env.bash")
    test_script = load_txt("scripts/test.bash")
    flake_script = load_txt("scripts/flake.bash")
    run_script = load_txt("scripts/run.bash")

    assert "UV_NO_SYNC=1" in env_script
    assert "uv_run --with poetry poetry lock" in sync_script
    assert "uv_run --with poetry poetry check" in sync_script
    assert 'uv_run pytest "${PYTEST_ARGS[@]}"' in test_script
    assert 'uv_run black "${PATHS[@]}"' in flake_script
    assert "enable_heavenbase_override" in run_script


def test_uv_run_sets_no_sync_for_active_heavenbase_override(tmp_path) -> None:
    root = pj(tmp_path, "repo")
    source = pj(tmp_path, "HeavenBase")
    touch_dir(pj(source, "src", "heavenbase"))
    save_txt("[project]\nname = 'heavenbase'\n", pj(source, "pyproject.toml"))
    probe_python = pj(root, ".venv", "bin", "python")
    touch_dir(pj(root, ".venv", "bin"))
    save_txt("#!/usr/bin/env bash\nexit 0\n", probe_python)
    cmd(["chmod", "+x", probe_python], check=True)
    marker = pj(root, ".venv", ".paradev-heavenbase-source")
    save_txt(f"{source}\n", marker)
    fake_uv = pj(tmp_path, "uv")
    save_txt(
        "#!/usr/bin/env bash\nprintf 'no-sync=%s\\n' \"${UV_NO_SYNC:-unset}\"\nprintf '%s\\n' \"$@\"\n",
        fake_uv,
    )
    cmd(["chmod", "+x", fake_uv], check=True)

    output = cmd(
        [
            "bash",
            "-c",
            'unset UV_NO_SYNC; ROOT="$1"; UV_BIN="$2"; source "$3"; uv_run pytest -q',
            "test-uv-run",
            root,
            fake_uv,
            pj("scripts", "_env.bash", abs=True),
        ],
        check=True,
        include="out",
    )

    assert output.splitlines() == ["no-sync=1", "run", "pytest", "-q"]


def test_uv_first_preference_uses_override_venv_python(tmp_path) -> None:
    root = pj(tmp_path, "repo")
    source = pj(tmp_path, "HeavenBase")
    touch_dir(pj(source, "src", "heavenbase"))
    save_txt("[project]\nname = 'heavenbase'\n", pj(source, "pyproject.toml"))
    python = pj(root, ".venv", "bin", "python")
    touch_dir(pj(root, ".venv", "bin"))
    save_txt(
        '#!/usr/bin/env bash\nif [[ "$1" == "-c" ]]; then exit 0; fi\nprintf \'override-python\\n\'\n',
        python,
    )
    cmd(["chmod", "+x", python], check=True)
    save_txt(f"{source}\n", pj(root, ".venv", ".paradev-heavenbase-source"))

    output = cmd(
        [
            "bash",
            "-c",
            'ROOT="$1"; REPO_PYTHON_PREFERENCE=uv-first; source "$2"; run_python -V',
            "test-uv-first",
            root,
            pj("scripts", "_env.bash", abs=True),
        ],
        check=True,
        include="out",
    )

    assert output == "override-python"


def test_uv_run_ignores_override_marker_when_import_origin_does_not_match(tmp_path) -> None:
    root = pj(tmp_path, "repo")
    source = pj(tmp_path, "HeavenBase")
    touch_dir(pj(source, "src", "heavenbase"))
    save_txt("[project]\nname = 'heavenbase'\n", pj(source, "pyproject.toml"))
    probe_python = pj(root, ".venv", "bin", "python")
    touch_dir(pj(root, ".venv", "bin"))
    save_txt("#!/usr/bin/env bash\nexit 1\n", probe_python)
    cmd(["chmod", "+x", probe_python], check=True)
    save_txt(f"{source}\n", pj(root, ".venv", ".paradev-heavenbase-source"))
    fake_uv = pj(tmp_path, "uv")
    save_txt(
        "#!/usr/bin/env bash\nprintf 'no-sync=%s\\n' \"${UV_NO_SYNC:-unset}\"\nprintf '%s\\n' \"$@\"\n",
        fake_uv,
    )
    cmd(["chmod", "+x", fake_uv], check=True)

    output = cmd(
        [
            "bash",
            "-c",
            'unset UV_NO_SYNC; ROOT="$1"; UV_BIN="$2"; source "$3"; uv_run pytest -q',
            "test-mismatched-import",
            root,
            fake_uv,
            pj("scripts", "_env.bash", abs=True),
        ],
        check=True,
        include="out",
    )

    assert output.splitlines() == ["no-sync=unset", "run", "pytest", "-q"]


def test_uv_run_ignores_stale_heavenbase_override_marker(tmp_path) -> None:
    root = pj(tmp_path, "repo")
    marker = pj(root, ".venv", ".paradev-heavenbase-source")
    touch_dir(pj(root, ".venv"))
    save_txt(f"{pj(tmp_path, 'missing-heavenbase')}\n", marker)
    fake_uv = pj(tmp_path, "uv")
    save_txt(
        "#!/usr/bin/env bash\nprintf 'no-sync=%s\\n' \"${UV_NO_SYNC:-unset}\"\nprintf '%s\\n' \"$@\"\n",
        fake_uv,
    )
    cmd(["chmod", "+x", fake_uv], check=True)

    output = cmd(
        [
            "bash",
            "-c",
            'unset UV_NO_SYNC; ROOT="$1"; UV_BIN="$2"; source "$3"; uv_run pytest -q',
            "test-stale-marker",
            root,
            fake_uv,
            pj("scripts", "_env.bash", abs=True),
        ],
        check=True,
        include="out",
    )

    assert output.splitlines() == ["no-sync=unset", "run", "pytest", "-q"]
