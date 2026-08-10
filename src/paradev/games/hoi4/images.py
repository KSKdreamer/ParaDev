"""HOI4 image decoding and preview helpers."""

from __future__ import annotations

import binascii
import struct
import zlib
from pathlib import Path
from typing import NamedTuple


class RgbaImage(NamedTuple):
    """Decoded RGBA image payload."""

    width: int
    height: int
    rgba: bytes


def dds_to_png_bytes(source_file: Path) -> bytes:
    """Return a PNG preview for a supported HOI4 DDS image."""

    image = decode_dds_image(source_file)
    return rgba_to_png_bytes(image.width, image.height, image.rgba)


def tga_to_png_bytes(source_file: Path) -> bytes:
    """Return a PNG preview for a supported HOI4 TGA image.

    Args:
        source_file: TGA source image to decode.

    Returns:
        PNG bytes encoded from the decoded RGBA pixels.

    Raises:
        ValueError: If the file is not a supported uncompressed true-color TGA.
    """

    image = decode_tga_image(source_file)
    return rgba_to_png_bytes(image.width, image.height, image.rgba)


def write_dds_preview_png(source_file: Path, target: Path) -> None:
    """Write a PNG preview decoded from a supported HOI4 DDS image."""

    target.write_bytes(dds_to_png_bytes(source_file))


def write_tga_preview_png(source_file: Path, target: Path) -> None:
    """Write a PNG preview decoded from a supported HOI4 TGA image.

    Args:
        source_file: TGA source image to decode.
        target: PNG target path.

    Raises:
        ValueError: If the file is not a supported uncompressed true-color TGA.
    """

    target.write_bytes(tga_to_png_bytes(source_file))


def decode_dds_image(source_file: Path) -> RgbaImage:
    """Decode the DDS formats used by PIHC/HOI4 interface icons."""

    payload = source_file.read_bytes()
    header = payload[:128]
    if len(header) < 128 or header[:4] != b"DDS ":
        raise ValueError(f"DDS file has invalid header: {source_file}")
    _header_size, _flags, height, width, pitch_or_linear_size, _depth, _mipmap_count = struct.unpack_from("<7I", header, 4)
    _pf_size, _pf_flags, fourcc_bytes, rgb_bit_count, r_mask, g_mask, b_mask, a_mask = struct.unpack_from("<II4sIIIII", header, 76)
    fourcc = fourcc_bytes.rstrip(b"\x00").decode("ascii", errors="replace")
    body = payload[128:]
    if not fourcc and rgb_bit_count == 32:
        pitch = pitch_or_linear_size if pitch_or_linear_size >= width * 4 else width * 4
        return RgbaImage(width=width, height=height, rgba=_decode_dds_rgb32(body, width, height, pitch, r_mask, g_mask, b_mask, a_mask))
    if fourcc == "DXT5":
        return RgbaImage(width=width, height=height, rgba=_decode_dds_dxt5(body, width, height))
    raise ValueError(f"Unsupported HOI4 preview DDS format {fourcc or rgb_bit_count}: {source_file}")


def decode_tga_image(source_file: Path) -> RgbaImage:
    """Decode the TGA formats used by PIHC/HOI4 flag images.

    Args:
        source_file: TGA source image to decode.

    Returns:
        Decoded RGBA image in top-left row order.

    Raises:
        ValueError: If the TGA header or pixel format is unsupported.
    """

    payload = source_file.read_bytes()
    header = payload[:18]
    if len(header) < 18:
        raise ValueError(f"TGA file has invalid header: {source_file}")

    id_length = header[0]
    color_map_type = header[1]
    image_type_id = header[2]
    width = header[12] | (header[13] << 8)
    height = header[14] | (header[15] << 8)
    bits_per_pixel = header[16]
    descriptor = header[17]
    if color_map_type != 0 or image_type_id != 2 or bits_per_pixel not in {24, 32} or width <= 0 or height <= 0:
        raise ValueError(f"Unsupported HOI4 preview TGA format {image_type_id}/{bits_per_pixel}: {source_file}")

    bytes_per_pixel = bits_per_pixel // 8
    data_offset = 18 + id_length
    data_size = width * height * bytes_per_pixel
    body = payload[data_offset : data_offset + data_size]
    if len(body) < data_size:
        raise ValueError(f"TGA data ended before all pixels were decoded: {source_file}")

    return RgbaImage(width=width, height=height, rgba=_decode_tga_true_color(body, width, height, bytes_per_pixel, descriptor))


def rgba_to_png_bytes(width: int, height: int, rgba: bytes) -> bytes:
    """Encode raw RGBA bytes as a PNG image."""

    rows = bytearray()
    row_size = width * 4
    for y in range(height):
        rows.append(0)
        rows.extend(rgba[y * row_size : (y + 1) * row_size])
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + _png_chunk(b"IDAT", zlib.compress(bytes(rows)))
        + _png_chunk(b"IEND", b"")
    )


def _decode_dds_rgb32(body: bytes, width: int, height: int, pitch: int, r_mask: int, g_mask: int, b_mask: int, a_mask: int) -> bytes:
    out = bytearray(width * height * 4)
    for y in range(height):
        row_offset = y * pitch
        for x in range(width):
            pixel = struct.unpack_from("<I", body, row_offset + x * 4)[0]
            out_offset = (y * width + x) * 4
            out[out_offset] = _mask_channel(pixel, r_mask, 0)
            out[out_offset + 1] = _mask_channel(pixel, g_mask, 0)
            out[out_offset + 2] = _mask_channel(pixel, b_mask, 0)
            out[out_offset + 3] = _mask_channel(pixel, a_mask, 255)
    return bytes(out)


def _mask_channel(pixel: int, mask: int, default: int) -> int:
    if mask == 0:
        return default
    shift = (mask & -mask).bit_length() - 1
    bits = mask.bit_count()
    value = (pixel & mask) >> shift
    return (value * 255) // ((1 << bits) - 1)


def _decode_tga_true_color(body: bytes, width: int, height: int, bytes_per_pixel: int, descriptor: int) -> bytes:
    out = bytearray(width * height * 4)
    origin_top = bool(descriptor & 0x20)
    origin_right = bool(descriptor & 0x10)
    for source_y in range(height):
        target_y = source_y if origin_top else height - 1 - source_y
        for source_x in range(width):
            target_x = width - 1 - source_x if origin_right else source_x
            source_offset = (source_y * width + source_x) * bytes_per_pixel
            target_offset = (target_y * width + target_x) * 4
            out[target_offset] = body[source_offset + 2]
            out[target_offset + 1] = body[source_offset + 1]
            out[target_offset + 2] = body[source_offset]
            out[target_offset + 3] = body[source_offset + 3] if bytes_per_pixel == 4 else 255
    return bytes(out)


def _decode_dds_dxt5(body: bytes, width: int, height: int) -> bytes:
    out = bytearray(width * height * 4)
    blocks_wide = (width + 3) // 4
    blocks_high = (height + 3) // 4
    offset = 0
    for block_y in range(blocks_high):
        for block_x in range(blocks_wide):
            block = body[offset : offset + 16]
            if len(block) < 16:
                raise ValueError("DXT5 DDS data ended in the middle of a block.")
            offset += 16
            alpha_palette = _dxt5_alpha_palette(block[0], block[1])
            alpha_bits = int.from_bytes(block[2:8], "little")
            color_palette = _dxt_color_palette(struct.unpack_from("<H", block, 8)[0], struct.unpack_from("<H", block, 10)[0])
            color_bits = struct.unpack_from("<I", block, 12)[0]
            for local_y in range(4):
                y = block_y * 4 + local_y
                if y >= height:
                    continue
                for local_x in range(4):
                    x = block_x * 4 + local_x
                    if x >= width:
                        continue
                    index = local_y * 4 + local_x
                    r, g, b = color_palette[(color_bits >> (2 * index)) & 0b11]
                    alpha = alpha_palette[(alpha_bits >> (3 * index)) & 0b111]
                    out_offset = (y * width + x) * 4
                    out[out_offset : out_offset + 4] = bytes((r, g, b, alpha))
    return bytes(out)


def _dxt5_alpha_palette(alpha_0: int, alpha_1: int) -> tuple[int, ...]:
    if alpha_0 > alpha_1:
        return (
            alpha_0,
            alpha_1,
            (6 * alpha_0 + alpha_1) // 7,
            (5 * alpha_0 + 2 * alpha_1) // 7,
            (4 * alpha_0 + 3 * alpha_1) // 7,
            (3 * alpha_0 + 4 * alpha_1) // 7,
            (2 * alpha_0 + 5 * alpha_1) // 7,
            (alpha_0 + 6 * alpha_1) // 7,
        )
    return (
        alpha_0,
        alpha_1,
        (4 * alpha_0 + alpha_1) // 5,
        (3 * alpha_0 + 2 * alpha_1) // 5,
        (2 * alpha_0 + 3 * alpha_1) // 5,
        (alpha_0 + 4 * alpha_1) // 5,
        0,
        255,
    )


def _dxt_color_palette(color_0: int, color_1: int) -> tuple[tuple[int, int, int], ...]:
    c0 = _rgb565(color_0)
    c1 = _rgb565(color_1)
    if color_0 > color_1:
        return (c0, c1, _mix_rgb(c0, c1, 2, 1, 3), _mix_rgb(c0, c1, 1, 2, 3))
    return (c0, c1, _mix_rgb(c0, c1, 1, 1, 2), (0, 0, 0))


def _rgb565(value: int) -> tuple[int, int, int]:
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return ((r * 255) // 31, (g * 255) // 63, (b * 255) // 31)


def _mix_rgb(left: tuple[int, int, int], right: tuple[int, int, int], left_weight: int, right_weight: int, divisor: int) -> tuple[int, int, int]:
    return tuple((left[index] * left_weight + right[index] * right_weight) // divisor for index in range(3))


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)


__all__ = [
    "RgbaImage",
    "dds_to_png_bytes",
    "decode_dds_image",
    "decode_tga_image",
    "rgba_to_png_bytes",
    "tga_to_png_bytes",
    "write_dds_preview_png",
    "write_tga_preview_png",
]
