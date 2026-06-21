"""UI: a UIList of versions and an N-panel in the 3D viewport."""

import bpy


class MESHVER_UL_versions(bpy.types.UIList):
    """List of mesh versions for the active object."""

    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        obj = context.active_object
        is_head = obj is not None and obj.mesh_versions_head == item.name

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.label(
                text="",
                icon='RADIOBUT_ON' if is_head else 'RADIOBUT_OFF',
            )
            row.prop(item, "name", text="", emboss=False)
            if item.created:
                sub = row.row()
                sub.alignment = 'RIGHT'
                sub.label(text=item.created)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='MESH_DATA')


class MESHVER_PT_panel(bpy.types.Panel):
    """Mesh Versions panel in the 3D viewport sidebar (N-panel)."""

    bl_label = "Mesh Versions"
    bl_idname = "MESHVER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Versions"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        if obj is None or obj.type != 'MESH':
            layout.label(text="Select a mesh object.", icon='INFO')
            return

        if context.mode != 'OBJECT':
            layout.label(text="Switch to Object Mode.", icon='INFO')

        row = layout.row()
        row.template_list(
            "MESHVER_UL_versions", "",
            obj, "mesh_versions",
            obj, "mesh_versions_index",
            rows=4,
        )

        col = row.column(align=True)
        col.operator("mesh_version.commit", text="", icon='ADD')
        col.operator("mesh_version.delete", text="", icon='REMOVE')
        col.separator()
        col.operator("mesh_version.update", text="", icon='FILE_REFRESH')
        col.operator("mesh_version.rename", text="", icon='GREASEPENCIL')

        layout.operator("mesh_version.checkout", icon='IMPORT')

        if obj.mesh_versions_head:
            layout.label(text=f"On: {obj.mesh_versions_head}", icon='RADIOBUT_ON')

        # Show the selected version's note, if any.
        idx = obj.mesh_versions_index
        if 0 <= idx < len(obj.mesh_versions):
            note = obj.mesh_versions[idx].note
            if note:
                box = layout.box()
                box.label(text=note, icon='TEXT')


classes = (
    MESHVER_UL_versions,
    MESHVER_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
