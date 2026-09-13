# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
import struct
import tempfile
from pathlib import Path
import unittest
from tests.model_fixtures import textured_triangle
from tests.texture_fixtures import _make_texture
from dks_patch_builder.model_packages.reader import read_model_package,ModelPackageError
from dks_patch_builder.model_packages._core import nif,embedded_texture,editing,package
from dks_patch_builder.model_packages._core.animation_editing import append_blocks
from dks_patch_builder.model_packages._core.controller import Preview
from dks_patch_builder.model_packages._core.replay import PackageCorpus


class EmbeddedNormalTests(unittest.TestCase):
    def test_geometry_change_is_not_a_normal_pixel_edit(self):
        raw=textured_triangle(normal=True);doc=nif.parse(raw)
        source=bytearray(doc.body(4));source[12]=0;struct.pack_into('<i',source,17,5)
        renderer=nif.parse(_make_texture(4,((4,4),))).body(0)
        raw=append_blocks(raw,{4:bytes(source)},[('NiPersistentSrcTextureRendererData',renderer)])
        geometry,_=editing.edit_geometry(raw,{0:dict(vertices=[(0,0,.2),(1,0,0),(0,1,0)])})
        pixels=embedded_texture.edit(geometry,4,bytes((255,0,0,255))*16,(4,4),profile='raw')
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.d2model'
            for current,allowed in ((geometry,True),(pixels,False)):
                s=package.Source('model.item','Synthetic.dv2','a'*64,current,original_payload=raw)
                p=Preview(PackageCorpus([s]));p.open_model(s);p.set_texture(4,s)
                path.write_bytes(p.package())
                if allowed:self.assertEqual(len(read_model_package(path).changed),1)
                else:
                    with self.assertRaisesRegex(ModelPackageError,'Normal-map pixel'):read_model_package(path)
