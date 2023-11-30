import json
import bpy
from bpy.types import Operator, Context, Object
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


bl_info = {
    'name': 'Import & Update Maya Skin Weights (.json)',
    'description': 'Update the skin weights of the currently selected object with those of a maya skin cluster',
    'version': (0, 1),
    'blender': (2, 80, 0),
    'location': 'File > Import > RPM Update Skin Weights (.json)',
    'wiki_url': 'https://github.com/readyplayerme/blender-addon-import-skin-weights',
    'category': 'Import',
}

NAME = bl_info["name"]
DESCRIPTION = bl_info["description"]


def update_vertex_weights(obj: Object, filepath: str):
    with open(filepath) as f:
        skin_weights_data = json.load(f)
        weights = skin_weights_data['deformerWeight']['weights']

        bone_name2vertex_weights = {}
        for weight in weights:
            bone_name = weight['source']

            vertex_weights = bone_name2vertex_weights.setdefault(bone_name, [])
            vertex_weights += weight['points']

        for bone_name, vertices in bone_name2vertex_weights.items():
            if vertex_group := obj.vertex_groups.get(bone_name):
                obj.vertex_groups.remove(vertex_group)

            vertex_group = obj.vertex_groups.new(name=bone_name)

            for vertex in vertices:
                vertex_group.add([vertex['index']], vertex['value'], 'REPLACE')


class UpdateWeights(Operator, ImportHelper):

    bl_options = {'REGISTER', 'INTERNAL'}
    bl_idname = 'rpm.update_skin_weights'
    bl_label = 'Update Weights'
    bl_description = DESCRIPTION

    filter_glob: StringProperty(
        default='*.json',
        options={'HIDDEN'},
    )
    directory: StringProperty(
        subtype='DIR_PATH',
    )

    def execute(self, context: Context):
        active_object: Object = context.active_object

        if not active_object:
            self.report({'ERROR'}, 'No Object Selected!')
            return {'CANCELLED'}

        if active_object.type != 'MESH':
            self.report({'ERROR'}, 'No Mesh Object Selected!')
            return {'CANCELLED'}

        update_vertex_weights(active_object, self.filepath)
        return {'FINISHED'}


def import_menu(self, context: Context):
    self.layout.operator(UpdateWeights.bl_idname, text=NAME)


classes = (
    UpdateWeights,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_import.append(import_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(import_menu)
