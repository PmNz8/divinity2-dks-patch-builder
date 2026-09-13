# SPDX-FileCopyrightText: 2026 PmNz8
# SPDX-License-Identifier: AGPL-3.0-only
"""Read complete native model packages and expose only verified changed bytes."""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import io
from pathlib import Path
import zipfile

from ..handlers.base import CompiledResource, HandlerError
from ..package import _read_bounded, _reject_link_components, _normalize_logical_path
from ._core import package as core_package

ASSET_TYPE = 'model.d2model'


class ModelPackageError(HandlerError):
    """A model package is unsupported, inconsistent or unsafe to use."""


@dataclass(frozen=True)
class ModelResource:
    logical_path: str
    archive_name: str
    archive_sha256: str
    original_sha256: str
    original_size: int
    current_sha256: str
    roles: tuple[str, ...]
    compiled: CompiledResource = field(repr=False)


@dataclass(frozen=True)
class ModelPackage:
    path: Path
    sha256: str
    schema: str
    primary: str
    resources: tuple[ModelResource, ...]
    warnings: tuple[str, ...]

    @property
    def changed(self) -> tuple[ModelResource, ...]:
        return tuple(r for r in self.resources if r.compiled.payload_changed)

    def summary(self) -> dict:
        return dict(package=str(self.path),sha256=self.sha256,schema=self.schema,
                    primary=self.primary,changed_resources=len(self.changed),
                    unchanged_resources=len(self.resources)-len(self.changed),warnings=list(self.warnings),
                    resources=[dict(path=r.logical_path,roles=list(r.roles),changed=r.compiled.payload_changed,
                                    size=r.compiled.compiled_size,sha256=r.current_sha256,
                                    original_sha256=r.original_sha256,archive=r.archive_name)
                               for r in self.resources])


def _path(value: str) -> str:
    if not isinstance(value,str) or any(ord(c)<32 for c in value):
        raise ModelPackageError('Invalid model logical path')
    return _normalize_logical_path(value,'model package path')


def read_model_package(path: str | Path) -> ModelPackage:
    """Validate archive, source/native edit spans and full preview assembly.

    No extraction, re-encoding or writing. Preview choices are not game-reference
    changes. Immutable compiled bytes are deliberately separate from originals.
    """
    path=Path(path).absolute()
    try:
        if path.suffix.casefold()!='.d2model': raise ModelPackageError('Choose a .d2model file')
        _reject_link_components(path,'model package')
        raw=_read_bounded(path,'model package',core_package.MAX_PACKAGE+16*1024*1024)
        manifest=core_package.verify(raw)
        package_hash=hashlib.sha256(raw).hexdigest()
        schema=manifest['schema']
        attachment=None
        cooked_native=None
        if schema in ('divinity2.model-source-package/3','divinity2.model-source-package/4'):
            from ._core import physics_carrier
            with zipfile.ZipFile(io.BytesIO(raw)) as carrier:
                attachment=physics_carrier.verify_members(carrier,manifest)
                cooked_native=attachment.native
                raw=attachment.model
            manifest=core_package.verify(raw)
        assembly=manifest.get('assembly')
        if not isinstance(assembly,dict): raise ModelPackageError('Model package requires a verified assembly')
        recipe=assembly['recipe']; primary=_path(manifest['primary'])
        roles: dict[str,set[str]]={primary.casefold():{'model'}}
        for role in ('skeleton','animation'):
            if recipe[role] is not None:
                roles.setdefault(_path(recipe[role]['resource']).casefold(),set()).add(role)
        textures={row['block']:_path(row['resource']).casefold() for row in recipe['textures']}
        for name in textures.values(): roles.setdefault(name,set()).add('texture')
        normal_sources={}
        for component in assembly['components']:
            slots=component['texturing']['slots'] if component['texturing'] else {}
            if 'normal' in slots and slots['normal']['source'] in textures:
                block=slots['normal']['source']
                normal_sources.setdefault(textures[block],set()).add(block)
        warnings=['Only changed native resources are queued; preview pairing, visibility and normal settings do not rewrite game references.',
                  'Originals stay in the model package. Different same-path variants warn; recorded source identity and pre-save drift remain guarded. Game compatibility is not certified.']
        warnings+=['Unresolved preview dependency: '+str(w) for w in assembly.get('unresolved',[])]
        if assembly.get('container'):
            warnings.append('Embedded model target: '+primary+' (whole CAT/ITEM; not its external mesh label).')
            error=assembly['container'].get('animation_preview_error')
            if error:
                warnings.append('Animation preview unavailable; native clips retained unchanged: '+error)
        resources=[]
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            static_normal_edits=False
            if primary.casefold().endswith('.item'):
                from ._core import item_editing
                primary_row=next(r for r in manifest['resources'] if _path(r['logical_path']).casefold()==primary.casefold())
                try:
                    item_editing.layout(z.read(primary_row.get('original_member',primary_row['member'])))
                    static_normal_edits=True
                except ValueError:
                    pass
            for row in manifest['resources']:
                logical=_path(row['logical_path']); key=logical.casefold()
                if key not in roles: raise ModelPackageError('Unbound resource outside the model assembly: '+logical)
                extension=Path(logical).suffix.casefold()
                expected={'.nif','.cat','.item'} if 'model' in roles[key] else ({'.kf'} if 'animation' in roles[key] else {'.nif'})
                if extension not in expected: raise ModelPackageError('Unsupported model resource path/type: '+logical)
                archive=_path(row['archive_name'])
                if not archive.casefold().endswith('.dv2'): raise ModelPackageError('Invalid source archive identity')
                current=z.read(row['member']); original=z.read(row.get('original_member',row['member']))
                changed=current!=original
                if changed and key in normal_sources:
                    pixels_changed=True
                    if 'model' in roles[key]:
                        from ._core import embedded_texture,nif
                        old_doc,new_doc=nif.parse(original),nif.parse(current)
                        pixels_changed=False
                        for block in normal_sources[key]:
                            old_owner,_=embedded_texture.resource(original,block)
                            new_owner,_=embedded_texture.resource(current,block)
                            if old_owner!=new_owner or old_doc.body(old_owner)!=new_doc.body(new_owner):
                                pixels_changed=True
                    if pixels_changed and not static_normal_edits:
                        raise ModelPackageError('Normal-map pixel edits are outside the verified D2Model export scope: '+logical)
                    if pixels_changed:
                        warnings.append('Static ITEM normal-map raw pixels changed: '+logical+'; native channels preserved, normal convention/runtime appearance not certified.')
                compiled=CompiledResource(ASSET_TYPE,logical,logical,current,hashlib.sha256(current).hexdigest(),len(current),
                                          hashlib.sha256(original).hexdigest(),len(original),changed,'zlib')
                resources.append(ModelResource(logical,archive,row['archive_sha256'],compiled.template_sha256,len(original),
                                               compiled.compiled_sha256,tuple(sorted(roles[key])),compiled))
        if {r.logical_path.casefold() for r in resources}!=set(roles):
            raise ModelPackageError('Assembly refers to absent model resources')
        if attachment is not None:
            source=attachment.source
            logical=_path(source.logical_path)
            if logical.casefold() in {r.logical_path.casefold() for r in resources}:
                raise ModelPackageError('Physics path overlaps model resources')
            current=cooked_native
            original=source.payload
            compiled=CompiledResource(ASSET_TYPE,logical,logical,current,hashlib.sha256(current).hexdigest(),len(current),
                                      hashlib.sha256(original).hexdigest(),len(original),current!=original,'zlib')
            resources.append(ModelResource(logical,_path(source.archive_name),source.archive_sha256,
                                           compiled.template_sha256,len(original),compiled.compiled_sha256,
                                           ('physics_collision',),compiled))
            warnings.append('Physics imported as opaque bytes. Package integrity checked; physics content and game compatibility are NOT validated. Use a backed-up test save.')
        return ModelPackage(path,package_hash,schema,primary,tuple(resources),tuple(warnings))
    except ModelPackageError: raise
    except Exception as exc: raise ModelPackageError(f'Cannot verify model package: {exc}') from exc
