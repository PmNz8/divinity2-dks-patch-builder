# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Synthetic NIF/D2Model fixtures; no game data or parent-repository imports."""
import hashlib
import struct

from dks_patch_builder.model_packages._core.package import Source
from dks_patch_builder.model_packages._core.controller import Preview
from dks_patch_builder.model_packages._core.replay import PackageCorpus
from dks_patch_builder.model_packages._core.editing import edit_geometry
from dks_patch_builder.model_packages._core.nif import parse


def triangle():
    def pack(fmt, *values):
        return struct.pack('<' + fmt, *values)
    def string(value):
        return pack('I', len(value)) + value
    transform = (0,0,0,1,0,0,0,1,0,0,0,1,1)
    shape = pack('iIiH13fIi', -1,0,-1,0,*transform,0,-1)+pack('iiIiB',1,-1,0,-1,0)
    geo = (pack('iHBBB9fHBB',0,3,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0)
           + pack('4fH6fB',0,0,0,1,2,0,0,0,1,1,0,0)
           + pack('HiHIB3HH',0,-1,1,3,1,0,1,2,0))
    return (b'Gamebryo File Format, Version 20.3.0.9\n'
            + pack('IBIIH',0x14030009,1,0x30000,2,2)
            + string(b'NiTriShape')+string(b'NiTriShapeData')
            + pack('2H2I3I',0,1,len(shape),len(geo),0,0,0)+shape+geo+pack('Ii',1,0))


def package_bytes(archive_bytes, *, logical='Win32/triangle.nif', edited=True, archive='Models.dv2'):
    original = triangle()
    current = edit_geometry(original, {0: dict(vertices=[(0,0,.25),(1,0,0),(0,1,0)])})[0] if edited else original
    source = Source(logical, archive, hashlib.sha256(archive_bytes).hexdigest(), current,
                    original_payload=original if edited else None)
    preview = Preview(PackageCorpus([source]))
    preview.open_model(source)
    return preview.package(), current


def textured_triangle(*, normal=False):
    def pack(fmt, *values):
        return struct.pack('<' + fmt, *values)
    def string(value):
        return pack('I', len(value)) + value
    doc = parse(triangle())
    shape = doc.body(0)
    # Replace the original empty property list with material/texturing references.
    shape = shape[:66] + pack('I2i', 2, 2, 3) + shape[70:]
    material = pack('iIi14f', -1, 0, -1, *([1.] * 14))
    count = 7 if normal else 5
    texturing = pack('iIiHI', -1,0,-1,0,count)
    for index in range(count):
        texturing += pack('B', index == (6 if normal else 0))
        if index == (6 if normal else 0):
            texturing += pack('iHB',4,0,0)
    texturing += pack('I',0)
    texture = pack('iIiBii3I3B', -1,0,-1,1,0,-1,0,0,0,1,0,0)
    types = (b'NiTriShape',b'NiTriShapeData',b'NiMaterialProperty',b'NiTexturingProperty',b'NiSourceTexture')
    bodies = (shape,doc.body(1),material,texturing,texture)
    return (b'Gamebryo File Format, Version 20.3.0.9\n'
            + pack('IBIIH',0x14030009,1,0x30000,5,5)
            + b''.join(string(kind) for kind in types)
            + pack('5H5III',0,1,2,3,4,*(len(b) for b in bodies),1,11)
            + string(b'texture.tga') + pack('I',0)
            + b''.join(bodies)+pack('Ii',1,0))


def multi_package(archive_bytes, model, texture, *, changed_texture=True):
    from dks_patch_builder.model_packages._core.editing import edit_materials
    from dks_patch_builder.model_packages._core.texture_editing import edit_texture
    from dks_patch_builder.model_packages._core.assets import decode_image
    changed_model = edit_materials(model, {2: {'diffuse': (.5,.7,.9)}})
    image = decode_image(texture)
    changed_pixels = edit_texture(texture, bytes((160,40,90,255)) * (image.size[0]*image.size[1]),
                                  image.size, profile='raw') if changed_texture else texture
    sha = hashlib.sha256(archive_bytes).hexdigest()
    primary = Source('Win32/triangle.nif','Models.dv2',sha,changed_model,original_payload=model)
    tex = Source('Win32/texture.nif','Models.dv2',sha,changed_pixels,original_payload=texture)
    preview = Preview(PackageCorpus([primary,tex]))
    preview.open_model(primary)
    preview.set_texture(4,tex)
    return preview.package()
