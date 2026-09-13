"""Opaque native-file import with independent synthetic package envelopes."""
import copy, hashlib, io, json, tempfile, unittest, zipfile
from pathlib import Path
from tests.model_fixtures import triangle,package_bytes
from tests.synth_builder import build_synthetic
from dks_patch_builder.model_packages._core import package
from dks_patch_builder.model_packages.reader import read_model_package
from dks_patch_builder.model import DKSPatchBuilderModel
from dks_patch_builder.dv2lib import DV2Session

ORIGINAL=b'arbitrary original bytes, NOT valid physics'
PREPARED=b'\0\xffopaque replacement, NOT valid physics'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def carrier(archive,*,prepared=True,changed=True):
    inner=package_bytes(archive)[0];geometry=b'opaque working data; deliberately not JSON'
    source=dict(logical_path='Win32/physics.nxb',archive_name='Models.dv2',archive_sha256=digest(archive),sha256=digest(ORIGINAL),size=len(ORIGINAL),member='physics/originals/'+digest(ORIGINAL)+'.nxb')
    row=dict(role='physics_collision',source=source,geometry_member='physics/geometry/'+digest(geometry)+'.json',geometry_sha256=digest(geometry),geometry_size=len(geometry),coordinate_space='original_physics_asset_coordinates_after_source_poses',association='user_selected_candidate',native_state='original_nxb_preserved',requires_cooking=changed)
    doc=dict(schema='divinity2.model-source-package/'+('4' if prepared else '3'),model=dict(member='model.d2model',sha256=digest(inner),size=len(inner)),physics=row)
    members={'model.d2model':inner,source['member']:ORIGINAL,row['geometry_member']:geometry}
    if prepared:
        cooked=dict(member='physics/cooked/'+digest(PREPARED)+'.nxb',sha256=digest(PREPARED),size=len(PREPARED),geometry_sha256=digest(geometry),original_sha256=digest(ORIGINAL),recipe='independent-producer',tool_version='anything',helper_sha256='1'*64,runtime_sha256='2'*64)
        doc['cooking']=cooked;members[cooked['member']]=PREPARED
    return doc,members

def encode(doc,members):
    result=io.BytesIO()
    with zipfile.ZipFile(result,'w',compression=zipfile.ZIP_STORED) as z:
        z.writestr('manifest.json',json.dumps(doc))
        for n,raw in members.items():z.writestr(n,raw)
    return result.getvalue()

class OpaquePhysicsTests(unittest.TestCase):
    def setUp(self):
        self.archive=build_synthetic([(r'Win32\triangle.nif',triangle(),'zlib'),(r'Win32\physics.nxb',ORIGINAL,'zlib')],1)
    def test_arbitrary_native_and_geometry_bytes_are_not_parsed(self):
        doc,members=carrier(self.archive)
        self.assertEqual(package.verify(encode(doc,members)),doc)
    def test_normal_import_save_exact_and_cancel_atomic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);packed=root/'Packed';packed.mkdir()
            (packed/'Models.dv2').write_bytes(self.archive)
            (packed/'Patch.dv2').write_bytes(build_synthetic([('control',b'control','raw')],1))
            source=root/'model.d2model';raw=encode(*carrier(self.archive));source.write_bytes(raw)
            parsed=read_model_package(source)
            self.assertTrue(any('NOT validated' in w for w in parsed.warnings))
            dks=root/'DKS_Patch.dv2';model=DKSPatchBuilderModel();model.create_archive(packed,dks)
            self.assertEqual(model.import_model_package(source)['queued_count'],2)
            self.assertEqual(len(model.cancel(r'Win32\physics.nxb')),2)
            model.import_model_package(source);model.save_in_place()
            self.assertEqual(DV2Session(dks).read_entry_bytes(r'Win32\physics.nxb'),PREPARED)
            self.assertEqual((packed/'Models.dv2').read_bytes(),self.archive)
            self.assertEqual(source.read_bytes(),raw)
    def test_unchanged_v3_and_changed_v3_without_prepared_bytes(self):
        self.assertTrue(package.verify(encode(*carrier(self.archive,prepared=False,changed=False))))
        with self.assertRaisesRegex(ValueError,'separate cooker'):
            package.verify(encode(*carrier(self.archive,prepared=False,changed=True)))
    def test_tampered_members_rejected(self):
        doc,members=carrier(self.archive)
        for name in members:
            bad=dict(members);bad[name]+=b'x'
            with self.subTest(member=name),self.assertRaises(ValueError):package.verify(encode(doc,bad))
    def test_bad_envelope_and_bindings_rejected(self):
        doc,members=carrier(self.archive)
        for change in ('target','source','binding','hash','size','producer','bool'):
            bad=copy.deepcopy(doc)
            if change=='target':bad['physics']['source']['logical_path']='../escape.nxb'
            if change=='source':bad['physics']['source']['archive_sha256']='bad'
            if change=='binding':bad['cooking']['geometry_sha256']='0'*64
            if change=='hash':bad['cooking']['sha256']='0'*64
            if change=='size':bad['cooking']['size']=True
            if change=='producer':bad['cooking']['recipe']=[]
            if change=='bool':bad['physics']['requires_cooking']=1
            with self.subTest(change=change),self.assertRaises(ValueError):package.verify(encode(bad,members))
    def test_extra_member_rejected(self):
        doc,members=carrier(self.archive);members['extra']=b'x'
        with self.assertRaises(ValueError):package.verify(encode(doc,members))
    def test_nested_physics_rejected(self):
        doc,members=carrier(self.archive);nested=encode(doc,members)
        doc['model'].update(size=len(nested),sha256=digest(nested));members['model.d2model']=nested
        with self.assertRaisesRegex(ValueError,'one v1/v2'):package.verify(encode(doc,members))
    def test_no_native_parser_modules_in_product(self):
        core=Path(package.__file__).parent
        for name in ('physics','physics_nxu','physics_package','physics_cooked','physics_cooking','physics_triangle','physics_triangle_codec'):
            self.assertFalse((core/(name+'.py')).exists())
