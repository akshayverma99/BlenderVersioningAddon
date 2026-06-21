"""Data model for mesh versioning.

A version is an immutable snapshot of an object's Mesh datablock. We keep a
pointer to the snapshot datablock (kept alive with a fake user) plus some
metadata. The collection of versions lives on the Object itself, so it travels
with the object and serializes into the .blend automatically.
"""

import bpy


class MeshVersion(bpy.types.PropertyGroup):
    """A single named snapshot of an object's mesh data."""

    name: bpy.props.StringProperty(
        name="Name",
        description="Display name for this version",
        default="Version",
    )
    mesh: bpy.props.PointerProperty(
        name="Mesh",
        description="The immutable mesh snapshot for this version",
        type=bpy.types.Mesh,
    )
    created: bpy.props.StringProperty(
        name="Created",
        description="When this version was committed",
        default="",
    )
    note: bpy.props.StringProperty(
        name="Note",
        description="Optional commit message",
        default="",
    )


def register():
    bpy.utils.register_class(MeshVersion)

    bpy.types.Object.mesh_versions = bpy.props.CollectionProperty(
        type=MeshVersion,
        name="Mesh Versions",
    )
    bpy.types.Object.mesh_versions_index = bpy.props.IntProperty(
        name="Active Version Index",
        default=0,
    )
    bpy.types.Object.mesh_versions_head = bpy.props.StringProperty(
        name="Checked-out Version",
        description="Name of the version currently loaded into the working mesh",
        default="",
    )


def unregister():
    del bpy.types.Object.mesh_versions_head
    del bpy.types.Object.mesh_versions_index
    del bpy.types.Object.mesh_versions

    bpy.utils.unregister_class(MeshVersion)
