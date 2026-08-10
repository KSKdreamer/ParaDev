#!/usr/bin/env python3
"""Generate ParaDev logo PNGs."""

from __future__ import annotations

import argparse
import binascii
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass, replace
from enum import Enum
from pathlib import Path

Point = tuple[float, float]
Color = tuple[int, int, int, int]

PHI = (math.sqrt(5) - 1) / 2
SUPERSAMPLE = 3
LINE_STEP_RATIO = 0.16
TITLE = "ParaDev"
SIZES = (32, 64, 128, 256, 512, 1024, 2160)
BACKGROUNDS = ("squircle", "none")
TITLE_MODES = (False, True)
DESKTOP_LOGO_SIZE = 128
APP_ICON_THEME = "github"
DEFAULT_FONT_PATHS = (
    Path("/Users/magolor/Library/Fonts/Ironmonger Black Regular.otf"),
    Path.home() / "Library" / "Fonts" / "Ironmonger Black Regular.otf",
    Path("/Library/Fonts/Ironmonger Black Regular.otf"),
)


class HexPoint(Enum):
    TOP = "top"
    UPPER_RIGHT = "upper_right"
    LOWER_RIGHT = "lower_right"
    BOTTOM = "bottom"
    LOWER_LEFT = "lower_left"
    UPPER_LEFT = "upper_left"
    CENTER = "center"


@dataclass(frozen=True)
class Theme:
    label: str
    background: Color
    foreground: Color
    accent: Color


@dataclass(frozen=True)
class Options:
    size: int = 1024
    theme: str = "ollama"
    background: str = "squircle"
    title: bool = False
    font: Path | None = None


@dataclass(frozen=True)
class Segment:
    start: HexPoint
    end: HexPoint


THEMES: dict[str, Theme] = {
    "ollama": Theme(
        "ParaDev Light Mode (Ollama Theme)",
        background=(0xF7, 0xF4, 0xEF, 0xFF),
        foreground=(0x0E, 0x11, 0x18, 0xFF),
        accent=(0x2F, 0x6F, 0x68, 0xFF),
    ),
    "github": Theme(
        "Dark Mode (GitHub Soft Dark Theme)",
        background=(0x16, 0x1B, 0x22, 0xFF),
        foreground=(0xF6, 0xF6, 0xF6, 0xFF),
        accent=(0x58, 0xA6, 0xFF, 0xFF),
    ),
    "anthro": Theme(
        "Anthro Mode (Anthropic Theme)",
        background=(0xF4, 0xEF, 0xE6, 0xFF),
        foreground=(0x0E, 0x11, 0x18, 0xFF),
        accent=(0xC6, 0x61, 0x3F, 0xFF),
    ),
}


def point(center: Point, radius: float, angle: float) -> Point:
    return (center[0] + math.cos(angle) * radius, center[1] - math.sin(angle) * radius)


def validate_options(options: Options) -> None:
    if options.size <= 0:
        raise ValueError("size must be positive")
    if options.theme not in THEMES:
        raise ValueError(f"theme must be one of {', '.join(THEMES)}")
    if options.background not in BACKGROUNDS:
        raise ValueError(f"background must be one of {', '.join(BACKGROUNDS)}")


def hex_radius(options: Options) -> float:
    return options.size * PHI / 2


def stroke_width(size: int) -> float:
    return max(1.0, size * PHI * (1 - PHI) ** 3)


def hex_vertices(options: Options) -> dict[HexPoint, Point]:
    validate_options(options)
    center = (options.size / 2, options.size / 2)
    radius = hex_radius(options)
    return {
        HexPoint.TOP: point(center, radius, math.pi / 2),
        HexPoint.UPPER_RIGHT: point(center, radius, math.pi / 6),
        HexPoint.LOWER_RIGHT: point(center, radius, -math.pi / 6),
        HexPoint.BOTTOM: point(center, radius, -math.pi / 2),
        HexPoint.LOWER_LEFT: point(center, radius, -5 * math.pi / 6),
        HexPoint.UPPER_LEFT: point(center, radius, 5 * math.pi / 6),
        HexPoint.CENTER: center,
    }


def logo_segments(options: Options) -> tuple[Segment, ...]:
    validate_options(options)
    return (
        Segment(HexPoint.TOP, HexPoint.CENTER),
        Segment(HexPoint.CENTER, HexPoint.UPPER_LEFT),
        Segment(HexPoint.UPPER_LEFT, HexPoint.TOP),
        Segment(HexPoint.CENTER, HexPoint.LOWER_RIGHT),
        Segment(HexPoint.LOWER_RIGHT, HexPoint.BOTTOM),
        Segment(HexPoint.BOTTOM, HexPoint.CENTER),
        Segment(HexPoint.UPPER_LEFT, HexPoint.LOWER_LEFT),
        Segment(HexPoint.UPPER_RIGHT, HexPoint.LOWER_RIGHT),
    )


def triangle_centroid(a: Point, b: Point, c: Point) -> Point:
    return ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3)


def triangle_area(a: Point, b: Point, c: Point) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def draw_triangle(mask: bytearray, size: int, a: Point, b: Point, c: Point) -> None:
    area = triangle_area(a, b, c)
    if area == 0:
        return
    sign = 1 if area > 0 else -1
    left = max(0, math.floor(min(a[0], b[0], c[0])))
    right = min(size - 1, math.ceil(max(a[0], b[0], c[0])))
    top = max(0, math.floor(min(a[1], b[1], c[1])))
    bottom = min(size - 1, math.ceil(max(a[1], b[1], c[1])))
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            p = (x + 0.5, y + 0.5)
            if sign * triangle_area(a, b, p) >= 0 and sign * triangle_area(b, c, p) >= 0 and sign * triangle_area(c, a, p) >= 0:
                mask[y * size + x] = 0xFF


def draw_disk(mask: bytearray, size: int, center: Point, radius: float) -> None:
    cx, cy = center
    r2 = radius * radius
    for y in range(max(0, math.floor(cy - radius)), min(size - 1, math.ceil(cy + radius)) + 1):
        dy = y + 0.5 - cy
        remaining = r2 - dy * dy
        if remaining < 0:
            continue
        dx = math.sqrt(remaining)
        x0 = max(0, math.floor(cx - dx))
        x1 = min(size - 1, math.ceil(cx + dx))
        start = y * size + x0
        mask[start : start + x1 - x0 + 1] = b"\xff" * (x1 - x0 + 1)


def draw_line(mask: bytearray, size: int, start: Point, end: Point, stroke: float) -> None:
    distance = math.dist(start, end)
    count = max(1, math.ceil(distance / max(1.0, stroke * LINE_STEP_RATIO)))
    for index in range(count + 1):
        t = index / count
        draw_disk(mask, size, (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t), stroke / 2)


def downsample(mask: bytearray, size: int) -> bytearray:
    high = size * SUPERSAMPLE
    out = bytearray(size * size)
    samples = SUPERSAMPLE * SUPERSAMPLE
    for y in range(size):
        for x in range(size):
            total = 0
            for dy in range(SUPERSAMPLE):
                offset = (y * SUPERSAMPLE + dy) * high + x * SUPERSAMPLE
                total += sum(mask[offset : offset + SUPERSAMPLE])
            out[y * size + x] = round(total / samples)
    return out


def stroke_mask(size: int) -> bytearray:
    high = size * SUPERSAMPLE
    options = Options(size=high)
    vertices = hex_vertices(options)
    stroke = stroke_width(high)
    mask = bytearray(high * high)
    for segment in logo_segments(options):
        draw_line(mask, high, vertices[segment.start], vertices[segment.end], stroke)
    return downsample(mask, size)


def accent_mask(size: int) -> bytearray:
    high = size * SUPERSAMPLE
    options = Options(size=high)
    vertices = hex_vertices(options)
    mask = bytearray(high * high)
    draw_triangle(mask, high, vertices[HexPoint.TOP], vertices[HexPoint.CENTER], vertices[HexPoint.UPPER_LEFT])
    return downsample(mask, size)


def squircle_mask(size: int) -> bytearray:
    high = size * SUPERSAMPLE
    mask = bytearray(high * high)
    center = high / 2
    radius = high / 2
    for y in range(high):
        ny = abs((y + 0.5 - center) / radius)
        remaining = 1 - ny**4
        if remaining < 0:
            continue
        half = radius * remaining**0.25
        x0 = max(0, math.floor(center - half))
        x1 = min(high - 1, math.ceil(center + half))
        start = y * high + x0
        mask[start : start + x1 - x0 + 1] = b"\xff" * (x1 - x0 + 1)
    return downsample(mask, size)


def blend(top: Color, top_alpha: int, bottom: Color, bottom_alpha: int) -> Color:
    alpha = top_alpha + bottom_alpha * (255 - top_alpha) // 255
    if not alpha:
        return (0, 0, 0, 0)
    red = (top[0] * top_alpha + bottom[0] * bottom_alpha * (255 - top_alpha) // 255) // alpha
    green = (top[1] * top_alpha + bottom[1] * bottom_alpha * (255 - top_alpha) // 255) // alpha
    blue = (top[2] * top_alpha + bottom[2] * bottom_alpha * (255 - top_alpha) // 255) // alpha
    return (red, green, blue, alpha)


def compose_icon(options: Options) -> bytes:
    validate_options(options)
    theme = THEMES[options.theme]
    accent = accent_mask(options.size)
    lines = stroke_mask(options.size)
    bg = squircle_mask(options.size) if options.background == "squircle" else bytearray(options.size * options.size)
    rgba = bytearray(options.size * options.size * 4)
    for index, line_coverage in enumerate(lines):
        bg_alpha = round(theme.background[3] * bg[index] / 255)
        accent_alpha = round(theme.accent[3] * accent[index] / 255)
        line_alpha = round(theme.foreground[3] * line_coverage / 255)
        accented = blend(theme.accent, accent_alpha, theme.background, bg_alpha)
        pixel = blend(theme.foreground, line_alpha, accented, accented[3])
        offset = index * 4
        rgba[offset : offset + 4] = bytes(pixel)
    return bytes(rgba)


def chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(payload, binascii.crc32(kind)) & 0xFFFFFFFF)


def write_png(path: Path, size: int, rgba: bytes) -> None:
    rows = bytearray()
    stride = size * 4
    for y in range(size):
        rows.append(0)
        rows.extend(rgba[y * stride : (y + 1) * stride])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return parsed


def output_root() -> Path:
    return Path(__file__).resolve().parents[1] / "assets" / "paradev-logo"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def desktop_logo_root() -> Path:
    return repo_root() / "apps" / "desktop" / "src" / "assets" / "paradev-logo"


def desktop_icon_root() -> Path:
    return repo_root() / "apps" / "desktop" / "host"


def desktop_public_root() -> Path:
    return repo_root() / "apps" / "desktop" / "public"


def background_slug(value: str) -> str:
    return "transparent" if value == "none" else value


def output_path(options: Options) -> Path:
    kind = "title" if options.title else "mark"
    return output_root() / options.theme / f"paradev-logo-{options.theme}-{background_slug(options.background)}-{kind}-{options.size}.png"


def canvas_size(options: Options) -> tuple[int, int]:
    if options.title:
        return (round(options.size / (PHI * PHI * PHI)), options.size)
    return (options.size, options.size)


def title_text_width(options: Options) -> int:
    width, height = canvas_size(options)
    gap = round(height * (1 - PHI) ** 2)
    return width - height - (2 * gap)


def all_outputs() -> list[Options]:
    return [
        Options(size=size, theme=theme, background=background, title=title)
        for theme in THEMES
        for background in BACKGROUNDS
        for title in TITLE_MODES
        for size in SIZES
    ]


def desktop_logo_options() -> list[Options]:
    return [Options(size=DESKTOP_LOGO_SIZE, theme=theme, background="squircle", title=False) for theme in THEMES]


def app_icon_options() -> Options:
    return Options(size=1024, theme=APP_ICON_THEME, background="squircle", title=False)


def color_hex(color: Color) -> str:
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def find_magick() -> str:
    magick = shutil.which("magick") or shutil.which("convert")
    if magick is None:
        raise RuntimeError("ImageMagick is required for title variants; install magick or run mark-only generation")
    return magick


def find_iconutil() -> str | None:
    return shutil.which("iconutil")


def find_font(path: Path | None = None) -> Path:
    if path is not None:
        if path.exists():
            return path
        raise FileNotFoundError(f"font not found: {path}")
    env_path = os.environ.get("PARADEV_LOGO_FONT")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return candidate
    for candidate in DEFAULT_FONT_PATHS:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Ironmonger Black Regular font not found; set PARADEV_LOGO_FONT or pass --font")


def render_title_png(mark_path: Path, path: Path, options: Options) -> None:
    validate_options(options)
    width, height = canvas_size(options)
    gap = round(height * (1 - PHI) ** 2)
    text_x = height + gap
    text_width = title_text_width(options)
    text_height = round(height * PHI)
    text_y = round((height - text_height) / 2)
    point_size = max(1, round(height * (1 - PHI)))
    theme = THEMES[options.theme]
    magick = find_magick()
    font = find_font(options.font)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paradev-logo-") as temp_dir:
        text_path = Path(temp_dir) / "title.png"
        subprocess.run(
            [
                magick,
                "-background",
                "none",
                "-font",
                str(font),
                "-fill",
                color_hex(theme.foreground),
                "-size",
                f"{text_width}x{text_height}",
                "-gravity",
                "center",
                "-pointsize",
                str(point_size),
                f"label:{TITLE}",
                f"png32:{text_path}",
            ],
            check=True,
        )
        subprocess.run(
            [
                magick,
                "-size",
                f"{width}x{height}",
                "xc:none",
                str(mark_path),
                "-geometry",
                "+0+0",
                "-composite",
                str(text_path),
                "-geometry",
                f"+{text_x}+{text_y}",
                "-composite",
                f"png32:{path}",
            ],
            check=True,
        )


def generate_output(options: Options, refresh_mark: bool = True) -> Path:
    validate_options(options)
    path = output_path(options)
    mark_options = replace(options, title=False)
    mark_path = output_path(mark_options)
    if refresh_mark or not mark_path.exists():
        write_png(mark_path, mark_options.size, compose_icon(mark_options))
    if options.title:
        render_title_png(mark_path, path, options)
    else:
        path = mark_path
    return path


def manifest_record(options: Options, path: Path) -> dict[str, object]:
    width, height = canvas_size(options)
    theme = THEMES[options.theme]
    return {
        "theme": options.theme,
        "theme_label": theme.label,
        "background": options.background,
        "title": options.title,
        "width": width,
        "height": height,
        "foreground": color_hex(theme.foreground),
        "background_color": color_hex(theme.background),
        "accent": color_hex(theme.accent),
        "path": str(path.relative_to(output_root().parents[1])),
    }


def write_manifest(records: list[dict[str, object]]) -> Path:
    path = output_root() / "manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"title": TITLE, "phi": PHI, "outputs": records}, indent=2) + "\n", encoding="utf-8")
    return path


def copy_logo_asset(source: Path, target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target


def install_desktop_logo_assets() -> list[Path]:
    paths: list[Path] = []
    for options in desktop_logo_options():
        source = generate_output(options)
        paths.append(copy_logo_asset(source, desktop_logo_root() / f"paradev-logo-{options.theme}.png"))
    return paths


def make_ico(source: Path, target: Path) -> Path:
    magick = find_magick()
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([magick, str(source), "-define", "icon:auto-resize=256,128,64,48,32,16", str(target)], check=True)
    return target


def resize_png(source: Path, target: Path, size: int) -> Path:
    magick = find_magick()
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([magick, str(source), "-resize", f"{size}x{size}", f"png32:{target}"], check=True)
    return target


def make_icns(source: Path, target: Path) -> Path:
    iconutil = find_iconutil()
    if iconutil is None:
        raise RuntimeError("iconutil is required to generate the macOS .icns app icon")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="paradev-iconset-") as temp_dir:
        iconset = Path(temp_dir) / "icon.iconset"
        iconset.mkdir()
        for name, size in (
            ("icon_16x16.png", 16),
            ("icon_16x16@2x.png", 32),
            ("icon_32x32.png", 32),
            ("icon_32x32@2x.png", 64),
            ("icon_128x128.png", 128),
            ("icon_128x128@2x.png", 256),
            ("icon_256x256.png", 256),
            ("icon_256x256@2x.png", 512),
            ("icon_512x512.png", 512),
            ("icon_512x512@2x.png", 1024),
        ):
            resize_png(source, iconset / name, size)
        subprocess.run([iconutil, "-c", "icns", "-o", str(target), str(iconset)], check=True)
    return target


def install_desktop_app_icons() -> list[Path]:
    options = app_icon_options()
    source = generate_output(options)
    root = desktop_icon_root()
    icon_32 = generate_output(replace(options, size=32))
    icon_128 = generate_output(replace(options, size=128))
    icon_256 = generate_output(replace(options, size=256))
    paths = [
        copy_logo_asset(icon_32, root / "32x32.png"),
        copy_logo_asset(icon_128, root / "128x128.png"),
        copy_logo_asset(icon_256, root / "128x128@2x.png"),
        copy_logo_asset(source, root / "icon.png"),
    ]
    paths.append(make_ico(source, root / "icon.ico"))
    paths.append(make_icns(source, root / "icon.icns"))
    paths.append(make_ico(source, desktop_public_root() / "favicon.ico"))
    return paths


def install_desktop_assets() -> list[Path]:
    return install_desktop_logo_assets() + install_desktop_app_icons()


def generate_all(install_desktop: bool = True) -> list[Path]:
    records: list[dict[str, object]] = []
    paths: list[Path] = []
    for options in all_outputs():
        path = generate_output(options, refresh_mark=not options.title)
        paths.append(path)
        records.append(manifest_record(options, path))
    paths.append(write_manifest(records))
    if install_desktop:
        paths.extend(install_desktop_assets())
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate ParaDev logo PNGs.")
    parser.add_argument("--single", action="store_true", help="generate one output instead of the full matrix")
    parser.add_argument("--theme", choices=tuple(THEMES), default="ollama")
    parser.add_argument("--background", choices=BACKGROUNDS, default="squircle")
    parser.add_argument("--title", action="store_true", help="include the Ironmonger title lockup in --single mode")
    parser.add_argument("--size", type=positive_int, default=1024)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--skip-desktop-install", action="store_true", help="do not refresh desktop GUI and bundle icon assets")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.single:
        path = generate_output(Options(size=args.size, theme=args.theme, background=args.background, title=args.title, font=args.font))
        width, height = canvas_size(Options(size=args.size, theme=args.theme, background=args.background, title=args.title, font=args.font))
        print(f"wrote {path} ({width}x{height}, theme={args.theme}, background={args.background}, title={args.title})")
        return 0
    paths = generate_all(install_desktop=not args.skip_desktop_install)
    root = output_root().resolve()
    generated_count = sum(1 for path in paths if root in (path.resolve(), *path.resolve().parents))
    installed_count = len(paths) - generated_count
    if installed_count:
        print(f"wrote {generated_count} files under {root} and installed {installed_count} desktop assets")
    else:
        print(f"wrote {generated_count} files under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
