"""Operators: commit / checkout / rename / delete / update.

Core rule: commits are immutable. A commit copies the working mesh into a new
datablock with a fake user. Checkout assigns a *copy* of a snapshot back into
obj.data, so the snapshot itself is never mutated by subsequent edits.

All operators require Object Mode: you cannot reassign obj.data while the mesh is
in Edit Mode, and edit-mode changes aren't flushed to obj.data until you exit.
"""

from datetime import datetime

import bpy


def _poll_mesh_object(context):
    obj = context.active_object
    return (
        obj is not None
        and obj.type == 'MESH'
        and context.mode == 'OBJECT'
    )


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _unique_version_name(obj, desired):
    """Return a version name unique within this object's history."""
    existing = {v.name for v in obj.mesh_versions}
    if desired not in existing:
        return desired
    i = 2
    while f"{desired}.{i:03d}" in existing:
        i += 1
    return f"{desired}.{i:03d}"


class MESHVER_OT_commit(bpy.types.Operator):
    """Save the current mesh as a new named version"""

    bl_idname = "mesh_version.commit"
    bl_label = "Commit Version"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Name", default="Version")
    note: bpy.props.StringProperty(name="Note", default="")

    @classmethod
    def poll(cls, context):
        return _poll_mesh_object(context)

    def invoke(self, context, event):
        obj = context.active_object
        self.name = f"Version {len(obj.mesh_versions) + 1}"
        self.note = ""
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object

        snap = obj.data.copy()
        snap.use_fake_user = True

        version = obj.mesh_versions.add()
        version.name = _unique_version_name(obj, self.name.strip() or "Version")
        version.mesh = snap
        version.created = _now()
        version.note = self.note

        # Name the datablock to match for a tidy outliner.
        snap.name = f"{obj.name}_v_{version.name}"

        obj.mesh_versions_index = len(obj.mesh_versions) - 1
        obj.mesh_versions_head = version.name

        self.report({'INFO'}, f"Committed '{version.name}'")
        return {'FINISHED'}


class MESHVER_OT_checkout(bpy.types.Operator):
    """Load the selected version into the working mesh (discards uncommitted edits)"""

    bl_idname = "mesh_version.checkout"
    bl_label = "Checkout Version"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            _poll_mesh_object(context)
            and 0 <= obj.mesh_versions_index < len(obj.mesh_versions)
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        obj = context.active_object
        version = obj.mesh_versions[obj.mesh_versions_index]

        if version.mesh is None:
            self.report({'ERROR'}, f"Version '{version.name}' has no mesh data")
            return {'CANCELLED'}

        old = obj.data
        obj.data = version.mesh.copy()
        obj.data.use_fake_user = False
        obj.data.name = f"{obj.name}_working"

        # Drop the fake user on the previous working mesh if nothing else
        # references it, so it can be purged rather than lingering.
        if old.users == 0:
            old.use_fake_user = False

        obj.mesh_versions_head = version.name

        self.report({'INFO'}, f"Checked out '{version.name}'")
        return {'FINISHED'}


class MESHVER_OT_rename(bpy.types.Operator):
    """Rename the selected version"""

    bl_idname = "mesh_version.rename"
    bl_label = "Rename Version"
    bl_options = {'REGISTER', 'UNDO'}

    name: bpy.props.StringProperty(name="Name", default="")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            _poll_mesh_object(context)
            and 0 <= obj.mesh_versions_index < len(obj.mesh_versions)
        )

    def invoke(self, context, event):
        obj = context.active_object
        self.name = obj.mesh_versions[obj.mesh_versions_index].name
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        obj = context.active_object
        version = obj.mesh_versions[obj.mesh_versions_index]

        new_name = self.name.strip()
        if not new_name:
            self.report({'ERROR'}, "Name cannot be empty")
            return {'CANCELLED'}

        was_head = obj.mesh_versions_head == version.name

        # Temporarily clear so uniqueness check ignores the current name.
        old_name = version.name
        version.name = ""
        version.name = _unique_version_name(obj, new_name)

        if version.mesh is not None:
            version.mesh.name = f"{obj.name}_v_{version.name}"
        if was_head:
            obj.mesh_versions_head = version.name

        self.report({'INFO'}, f"Renamed '{old_name}' to '{version.name}'")
        return {'FINISHED'}


class MESHVER_OT_delete(bpy.types.Operator):
    """Delete the selected version"""

    bl_idname = "mesh_version.delete"
    bl_label = "Delete Version"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            _poll_mesh_object(context)
            and 0 <= obj.mesh_versions_index < len(obj.mesh_versions)
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        obj = context.active_object
        index = obj.mesh_versions_index
        version = obj.mesh_versions[index]
        name = version.name

        # Release the snapshot so orphan purge can reclaim it on save.
        if version.mesh is not None:
            version.mesh.use_fake_user = False

        if obj.mesh_versions_head == name:
            obj.mesh_versions_head = ""

        obj.mesh_versions.remove(index)
        obj.mesh_versions_index = min(index, len(obj.mesh_versions) - 1)

        self.report({'INFO'}, f"Deleted '{name}'")
        return {'FINISHED'}


class MESHVER_OT_update(bpy.types.Operator):
    """Overwrite the selected version with the current working mesh (amend)"""

    bl_idname = "mesh_version.update"
    bl_label = "Update Version"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (
            _poll_mesh_object(context)
            and 0 <= obj.mesh_versions_index < len(obj.mesh_versions)
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        obj = context.active_object
        version = obj.mesh_versions[obj.mesh_versions_index]

        snap = obj.data.copy()
        snap.use_fake_user = True
        snap.name = f"{obj.name}_v_{version.name}"

        old = version.mesh
        version.mesh = snap
        version.created = _now()

        if old is not None:
            old.use_fake_user = False

        self.report({'INFO'}, f"Updated '{version.name}'")
        return {'FINISHED'}


classes = (
    MESHVER_OT_commit,
    MESHVER_OT_checkout,
    MESHVER_OT_rename,
    MESHVER_OT_delete,
    MESHVER_OT_update,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
