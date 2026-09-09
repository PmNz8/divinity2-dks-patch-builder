"""Synthetic standalone texture wrapper fixture for Builder tests."""

import struct

from dks_patch_builder.codec import bc


def _make_texture(
    pixel_format: int,
    dimensions: tuple[tuple[int, int], ...] = ((8, 4), (4, 2), (2, 1)),
) -> bytes:
    compressed: list[bytes] = []
    for index, (width, height) in enumerate(dimensions):
        if pixel_format == bc.FORMAT_BC1:
            color = ((index + 1) * 0x20) & 0xFF
            rgba = bytes((color, 30, 200 - color, 255)) * (width * height)
            compressed.append(bc.encode_bc1_opaque(rgba, width, height))
        elif pixel_format == bc.FORMAT_BC3:
            rgba = bytes((50 + index, 120, 210, 20 + index * 50)) * (width * height)
            compressed.append(bc.encode_bc3(rgba, width, height))
        elif pixel_format == bc.FORMAT_BC2:
            blocks = ((width + 3) // 4) * ((height + 3) // 4)
            block = b"\xff" * 8 + struct.pack("<HHI", 0xF800, 0x07E0, 0)
            compressed.append(block * blocks)
        else:
            raise AssertionError(pixel_format)
    data = b"".join(compressed)
    descriptor = b"D" * 59
    body = bytearray(
        struct.pack("<I", pixel_format)
        + descriptor
        + bytes((len(dimensions),))
        + b"\0" * 7
    )
    cursor = 0
    for (width, height), mip in zip(dimensions, compressed, strict=True):
        body += struct.pack("<III", width, height, cursor)
        cursor += len(mip)
    body += struct.pack("<4I", len(data), len(data), 1, 3) + data
    output = bytearray(b"Gamebryo File Format, Version 20.3.0.9\n")
    output += struct.pack("<IBIIH", 0x14030009, 1, 0x00030000, 1, 1)
    type_bytes = b"NiPersistentSrcTextureRendererData"
    output += struct.pack("<I", len(type_bytes)) + type_bytes
    output += struct.pack("<H", 0)
    output += struct.pack("<I", len(body))
    output += struct.pack("<II", 0, 0)
    output += struct.pack("<I", 0)
    output += body
    output += struct.pack("<Ii", 1, 0)
    return bytes(output)
