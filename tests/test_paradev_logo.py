"""Tests for the ParaDev logo generator."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest

LOGO_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "logo.py"


def load_logo():
    spec = importlib.util.spec_from_file_location("paradev_logo", LOGO_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {LOGO_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ParaDevLogoTest(unittest.TestCase):
    def setUp(self) -> None:
        self.logo = load_logo()

    def test_theme_colors_are_paradox_foregrounds_with_named_backgrounds(self) -> None:
        self.assertEqual(tuple(self.logo.THEMES), ("ollama", "github", "anthro"))
        self.assertEqual(self.logo.THEMES["ollama"].foreground, (0x0E, 0x11, 0x18, 0xFF))
        self.assertEqual(self.logo.THEMES["github"].foreground, (0xF6, 0xF6, 0xF6, 0xFF))
        self.assertEqual(self.logo.THEMES["anthro"].foreground, (0x0E, 0x11, 0x18, 0xFF))
        self.assertEqual(self.logo.THEMES["github"].background, (0x16, 0x1B, 0x22, 0xFF))
        self.assertEqual(self.logo.THEMES["ollama"].accent, (0x2F, 0x6F, 0x68, 0xFF))
        self.assertEqual(self.logo.THEMES["github"].accent, (0x58, 0xA6, 0xFF, 0xFF))
        self.assertEqual(self.logo.THEMES["anthro"].accent, (0xC6, 0x61, 0x3F, 0xFF))

    def test_regular_hexagon_uses_phi_bounding_box_and_vertical_edges(self) -> None:
        options = self.logo.Options(size=1000, theme="ollama", background="squircle", title=False)
        vertices = self.logo.hex_vertices(options)
        xs = [point[0] for point in vertices.values()]
        ys = [point[1] for point in vertices.values()]

        self.assertAlmostEqual(max(ys) - min(ys), self.logo.PHI * options.size, places=7)
        self.assertAlmostEqual(vertices[self.logo.HexPoint.UPPER_LEFT][0], vertices[self.logo.HexPoint.LOWER_LEFT][0], places=7)
        self.assertAlmostEqual(vertices[self.logo.HexPoint.UPPER_RIGHT][0], vertices[self.logo.HexPoint.LOWER_RIGHT][0], places=7)
        self.assertLess(max(xs) - min(xs), max(ys) - min(ys))

    def test_hollow_mark_draws_only_two_triangles_and_vertical_edges(self) -> None:
        segments = self.logo.logo_segments(self.logo.Options(size=1000, theme="ollama", background="squircle", title=False))
        names = {(segment.start, segment.end) for segment in segments}

        self.assertEqual(
            names,
            {
                (self.logo.HexPoint.TOP, self.logo.HexPoint.CENTER),
                (self.logo.HexPoint.CENTER, self.logo.HexPoint.UPPER_LEFT),
                (self.logo.HexPoint.UPPER_LEFT, self.logo.HexPoint.TOP),
                (self.logo.HexPoint.CENTER, self.logo.HexPoint.LOWER_RIGHT),
                (self.logo.HexPoint.LOWER_RIGHT, self.logo.HexPoint.BOTTOM),
                (self.logo.HexPoint.BOTTOM, self.logo.HexPoint.CENTER),
                (self.logo.HexPoint.UPPER_LEFT, self.logo.HexPoint.LOWER_LEFT),
                (self.logo.HexPoint.UPPER_RIGHT, self.logo.HexPoint.LOWER_RIGHT),
            },
        )

    def test_all_outputs_cover_themes_backgrounds_titles_and_sizes(self) -> None:
        outputs = self.logo.all_outputs()

        self.assertEqual(len(outputs), len(self.logo.THEMES) * len(self.logo.BACKGROUNDS) * len(self.logo.TITLE_MODES) * len(self.logo.SIZES))
        self.assertTrue(any(option.title for option in outputs))
        self.assertTrue(any(not option.title for option in outputs))
        self.assertEqual({option.background for option in outputs}, set(self.logo.BACKGROUNDS))
        self.assertEqual({option.size for option in outputs}, set(self.logo.SIZES))

    def test_desktop_install_uses_squircle_marks_for_gui_and_github_app_icon(self) -> None:
        options = self.logo.desktop_logo_options()

        self.assertEqual([option.theme for option in options], ["ollama", "github", "anthro"])
        self.assertTrue(all(option.background == "squircle" for option in options))
        self.assertTrue(all(option.title is False for option in options))
        self.assertTrue(all(option.size == self.logo.DESKTOP_LOGO_SIZE for option in options))
        self.assertEqual(self.logo.app_icon_options().theme, "github")

    def test_render_has_squircle_background_and_hollow_foreground(self) -> None:
        options = self.logo.Options(size=128, theme="github", background="squircle", title=False)
        rgba = self.logo.compose_icon(options)
        pixels = [rgba[i : i + 4] for i in range(0, len(rgba), 4)]

        self.assertEqual(tuple(rgba[:4])[3], 0)
        center = (options.size // 2 * options.size + options.size // 2) * 4
        self.assertEqual(rgba[center + 3], 255)
        self.assertIn(bytes((0x16, 0x1B, 0x22, 0xFF)), pixels)
        self.assertIn(bytes((0xF6, 0xF6, 0xF6, 0xFF)), pixels)
        self.assertLess(sum(1 for pixel in pixels if pixel == bytes((0xF6, 0xF6, 0xF6, 0xFF))), options.size * options.size // 3)

    def test_render_fills_upper_left_triangle_under_hollow_edges(self) -> None:
        options = self.logo.Options(size=128, theme="anthro", background="squircle", title=False)
        rgba = self.logo.compose_icon(options)
        vertices = self.logo.hex_vertices(options)
        upper_fill = self.logo.triangle_centroid(
            vertices[self.logo.HexPoint.TOP],
            vertices[self.logo.HexPoint.CENTER],
            vertices[self.logo.HexPoint.UPPER_LEFT],
        )
        lower_empty = self.logo.triangle_centroid(
            vertices[self.logo.HexPoint.CENTER],
            vertices[self.logo.HexPoint.LOWER_RIGHT],
            vertices[self.logo.HexPoint.BOTTOM],
        )

        upper_offset = (round(upper_fill[1]) * options.size + round(upper_fill[0])) * 4
        lower_offset = (round(lower_empty[1]) * options.size + round(lower_empty[0])) * 4

        self.assertEqual(tuple(rgba[upper_offset : upper_offset + 4]), self.logo.THEMES["anthro"].accent)
        self.assertEqual(tuple(rgba[lower_offset : lower_offset + 4]), self.logo.THEMES["anthro"].background)

    def test_render_can_omit_squircle_background(self) -> None:
        options = self.logo.Options(size=128, theme="ollama", background="none", title=False)
        rgba = self.logo.compose_icon(options)
        pixels = [rgba[i : i + 4] for i in range(0, len(rgba), 4)]

        self.assertEqual(tuple(rgba[:4])[3], 0)
        self.assertIn(bytes((0x0E, 0x11, 0x18, 0xFF)), pixels)
        self.assertLess(sum(1 for pixel in pixels if pixel[3]), options.size * options.size // 3)

    def test_squircle_is_fourth_power_superellipse(self) -> None:
        mask = self.logo.squircle_mask(128)
        center = 64

        self.assertEqual(mask[center * 128 + center], 255)
        self.assertEqual(mask[0], 0)
        self.assertGreater(mask[center], 200)
        self.assertGreater(mask[center * 128], 200)

    def test_title_canvas_uses_phi_square_ratio(self) -> None:
        options = self.logo.Options(size=1000, theme="anthro", background="squircle", title=True)
        width, height = self.logo.canvas_size(options)

        self.assertEqual(height, 1000)
        self.assertEqual(width, round(1000 / (self.logo.PHI * self.logo.PHI * self.logo.PHI)))
        self.assertGreater(self.logo.title_text_width(options), 2500)


if __name__ == "__main__":
    unittest.main()
