"""Mesh Versioning add-on.

Gives a mesh object a git-like history of named snapshots: commit the current
mesh, keep editing, commit again, and checkout any earlier snapshot. Snapshots
are stored as Mesh datablocks (kept alive with a fake user) so they persist with
the .blend.

This is a Blender 4.2+ extension; metadata lives in blender_manifest.toml and
bl_info is intentionally omitted. Sibling modules are imported relatively.
"""

from . import properties
from . import operators
from . import ui

_modules = (properties, operators, ui)


def register():
    for module in _modules:
        module.register()


def unregister():
    for module in reversed(_modules):
        module.unregister()
