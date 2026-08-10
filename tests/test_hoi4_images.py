from pathlib import Path

import pytest

from paradev.games.hoi4.images import decode_tga_image, tga_to_png_bytes, write_tga_preview_png


def test_tga_preview_decoder_returns_top_left_rgba_pixels(tmp_path: Path) -> None:
    source = tmp_path / "flag.tga"
    source.write_bytes(
        bytes(
            [
                0,
                0,
                2,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                2,
                0,
                1,
                0,
                32,
                0x28,
                3,
                2,
                1,
                4,
                4,
                6,
                5,
                255,
            ]
        )
    )

    image = decode_tga_image(source)
    target = tmp_path / "preview.png"
    write_tga_preview_png(source, target)

    assert image.width == 2
    assert image.height == 1
    assert image.rgba == bytes([1, 2, 3, 4, 5, 6, 4, 255])
    assert target.read_bytes() == tga_to_png_bytes(source)
    assert target.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_tga_preview_decoder_rejects_unsupported_tga_kind(tmp_path: Path) -> None:
    source = tmp_path / "indexed.tga"
    source.write_bytes(bytes([0, 1, 1]) + (b"\x00" * 15))

    with pytest.raises(ValueError, match="Unsupported HOI4 preview TGA"):
        decode_tga_image(source)
