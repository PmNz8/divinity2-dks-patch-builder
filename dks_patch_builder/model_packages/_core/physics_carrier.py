# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Package-envelope integrity only. Native physics and geometry are opaque bytes.

No physics SDK, type catalog, native parser, geometry validator or cooker.
Hashes bind supplied members to the manifest; they do not establish correctness.
"""
from dataclasses import dataclass
import io
import json
import zipfile
from . import package

V3='divinity2.model-source-package/3'
V4='divinity2.model-source-package/4'

@dataclass(frozen=True)
class Carrier:
    source: package.Source
    native: bytes
    model: bytes

def fields(value,expected,label):
    if not isinstance(value,dict) or set(value)!=set(expected.split()):
        raise package.PackageError('Invalid '+label+' fields')

def verify_members(z,manifest):
    prepared=manifest.get('schema')==V4
    fields(manifest,'schema model physics'+(' cooking' if prepared else ''),'physics carrier')
    if manifest['schema'] not in (V3,V4):raise package.PackageError('Unsupported physics carrier')
    model=manifest['model'];row=manifest['physics']
    fields(model,'member sha256 size','nested model')
    fields(row,'role source geometry_member geometry_sha256 geometry_size coordinate_space association native_state requires_cooking','physics envelope')
    if (model['member']!='model.d2model' or row['role']!='physics_collision'
        or row['coordinate_space']!='original_physics_asset_coordinates_after_source_poses'
        or row['association']!='user_selected_candidate' or row['native_state']!='original_nxb_preserved'
        or type(row['requires_cooking']) is not bool):
        raise package.PackageError('Invalid physics envelope declaration')
    source=row['source']
    fields(source,'logical_path archive_name archive_sha256 member sha256 size','physics source')
    logical=package.logical_path(source['logical_path']);archive=package.logical_path(source['archive_name'])
    if not logical.lower().endswith('.nxb') or not archive.lower().endswith('.dv2'):
        raise package.PackageError('Physics target must name an NXB in a DV2')
    package._sha(source['archive_sha256'])
    for value in (source['sha256'],row['geometry_sha256']):package._sha(value)
    if (source['member']!='physics/originals/'+source['sha256']+'.nxb'
        or row['geometry_member']!='physics/geometry/'+row['geometry_sha256']+'.json'):
        raise package.PackageError('Invalid physics member path')
    def read(name,digest,size,limit):
        package._sha(digest)
        if type(size) is not int or not 0<size<=limit or z.getinfo(name).file_size!=size:
            raise package.PackageError('Invalid carrier member size')
        raw=z.read(name)
        if len(raw)!=size or package.digest(raw)!=digest:
            raise package.PackageError('Carrier member integrity mismatch')
        return raw
    expected={'manifest.json','model.d2model',source['member'],row['geometry_member']}
    cooked=manifest.get('cooking')
    if prepared:
        fields(cooked,'member sha256 size geometry_sha256 original_sha256 recipe tool_version helper_sha256 runtime_sha256','prepared file record')
        for key in ('sha256','geometry_sha256','original_sha256','helper_sha256','runtime_sha256'):package._sha(cooked[key])
        if any(not isinstance(cooked[k],str) or not 0<len(cooked[k])<=256 for k in ('recipe','tool_version')):
            raise package.PackageError('Invalid producer metadata')
        if (cooked['member']!='physics/cooked/'+cooked['sha256']+'.nxb'
            or cooked['original_sha256']!=source['sha256'] or cooked['geometry_sha256']!=row['geometry_sha256']):
            raise package.PackageError('Stale or invalid prepared-file binding')
        expected.add(cooked['member'])
    names=z.namelist()
    if len(names)!=len(set(names)) or set(names)!=expected:
        raise package.PackageError('Unexpected/duplicate physics carrier members')
    inner=read(model['member'],model['sha256'],model['size'],package.MAX_PACKAGE)
    # Permit exactly one inner visual package, not recursively nested carriers.
    with zipfile.ZipFile(io.BytesIO(inner)) as nested:
        if nested.getinfo('manifest.json').file_size>16*1024*1024:raise package.PackageError('Oversized inner manifest')
        doc=json.loads(nested.read('manifest.json'),object_pairs_hook=package._object)
    if not isinstance(doc,dict) or doc.get('schema') not in (package.SCHEMA,package.EDIT_SCHEMA):
        raise package.PackageError('Physics carrier requires one v1/v2 model package')
    package.verify(inner)
    original=read(source['member'],source['sha256'],source['size'],64*1024*1024)
    read(row['geometry_member'],row['geometry_sha256'],row['geometry_size'],32*1024*1024)
    # Geometry contents are not parsed; v3 contains only the original native file.
    if not prepared and row['requires_cooking']:
        raise package.PackageError('Working v3 has no prepared physics file; run the separate cooker and import v4')
    native=read(cooked['member'],cooked['sha256'],cooked['size'],64*1024*1024) if prepared else original
    return Carrier(package.Source(logical,archive,source['archive_sha256'],original),native,inner)
