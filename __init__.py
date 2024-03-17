import bpy
import os
import subprocess
import shutil

bl_info = {
    "name": "TexConv",
    "author": "Nomadic Jester",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Material > TexConv",
    "description": "Convert images to DDS format using TexConv",
    "category": "Material"
}

addon_dir = os.path.dirname(__file__)
texconv_exe = os.path.join(addon_dir, "texconv.exe")

# Function to convert image file to DDS format
def convert_to_dds(input_file, output_file, compression_format):
    command = [
        texconv_exe,
        "-nologo",
        "-pow2",
        "-f", compression_format,
        "-srgb", "off",  # Disable sRGB gamma correction
        "-y",
        "-ft", "DDS",
        input_file,
        "-o", os.path.dirname(output_file),
    ]
    subprocess.run(command, shell=True)

# Function to convert image file to PNG format
def convert_to_png(input_file, output_file):
    command = [
        texconv_exe,
        "-nologo",
        "-pow2",
        "-srgb", "on",  # Enable sRGB gamma correction
        "-y",
        "-ft", "PNG",
        input_file,
        "-o", os.path.dirname(output_file),
    ]
    subprocess.run(command, shell=True)

# Function to move DDS textures to the new folder
def move_dds_textures(blend_file_dir, dds_dir):
    for root, dirs, files in os.walk(blend_file_dir):
        for file in files:
            if file.lower().endswith('.dds'):
                shutil.move(os.path.join(root, file), os.path.join(dds_dir, file))

# Function to get the compression format from the material name
def get_compression_format_from_name(material_name):
    compression_formats = {
        "dxt1": "BC1_UNORM",
        "dxt3": "BC2_UNORM",
        "dxt5": "BC3_UNORM"
    }
    for key, value in compression_formats.items():
        if key in material_name.lower():
            return value
    return None

# GUI Panel
class ConvertToDDSPanel(bpy.types.Panel):
    bl_label = "TexConv"
    bl_idname = "OBJECT_PT_convert_to_dds"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="Compression Format:")
        layout.prop(scene, "compression_format", text="")

        row = layout.row()
        row.operator("object.convert_to_dds", text="Convert")
        row.operator("object.fix_mip_maps", text="Fix Mip Maps")

        layout.separator()

        layout.label(text="Folder Operations:")
        row = layout.row()
        row.prop(scene, "selected_folder", text="Folder")
        row.operator("object.fix_folder_mip_maps", text="Fix Folder Mip Maps")

# Operator to execute DDS conversion
class OBJECT_OT_ConvertToDDS(bpy.types.Operator):
    bl_idname = "object.convert_to_dds"
    bl_label = "Convert to DDS"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_object = context.active_object
        blend_file_dir = bpy.path.abspath("//")
        dds_dir = os.path.join(blend_file_dir, "dds-textures")
        if not os.path.exists(dds_dir):
            os.makedirs(dds_dir)

        for material_slot in selected_object.material_slots:
            material = material_slot.material
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image_path = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(image_path):
                            if image_path.lower().endswith('.dds'):
                                shutil.move(image_path, os.path.join(dds_dir, os.path.basename(image_path)))
                            else:
                                image_copy_path = os.path.join(blend_file_dir, os.path.basename(image_path))
                                shutil.copy2(image_path, image_copy_path)
                                dds_filename = os.path.splitext(os.path.basename(image_copy_path))[0] + ".dds"
                                dds_path = os.path.join(dds_dir, dds_filename)
                                material_compression_format = get_compression_format_from_name(material.name)
                                if material_compression_format:
                                    convert_to_dds(image_copy_path, dds_path, material_compression_format)
                                else:
                                    original_compression_format = get_compression_format_from_name(os.path.basename(image_path))
                                    if original_compression_format:
                                        convert_to_dds(image_copy_path, dds_path, original_compression_format)
                                    else:
                                        convert_to_dds(image_copy_path, dds_path, context.scene.compression_format)
                                node.image.filepath = bpy.path.relpath(dds_path)
                                bpy.data.images[node.image.name].name = dds_filename
                                os.remove(image_copy_path)

        self.report({'INFO'}, "DDS conversion complete.")
        return {'FINISHED'}

# Operator to fix mip maps
class OBJECT_OT_FixMipMaps(bpy.types.Operator):
    bl_idname = "object.fix_mip_maps"
    bl_label = "Fix Mip Maps"

    def execute(self, context):
        selected_object = context.active_object
        blend_file_dir = bpy.path.abspath("//")
        fixed_dds_dir = os.path.join(blend_file_dir, "fixed-dds-textures")
        if not os.path.exists(fixed_dds_dir):
            os.makedirs(fixed_dds_dir)

        for material_slot in selected_object.material_slots:
            material = material_slot.material
            if material and material.use_nodes:
                for node in material.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        image_path = bpy.path.abspath(node.image.filepath)
                        if os.path.exists(image_path) and image_path.lower().endswith('.dds'):
                            fixed_dds_path = os.path.join(fixed_dds_dir, os.path.basename(image_path))
                            temp_png_path = os.path.splitext(fixed_dds_path)[0] + ".png"
                            convert_to_png(image_path, temp_png_path)
                            material_compression_format = get_compression_format_from_name(material.name)
                            if material_compression_format:
                                convert_to_dds(temp_png_path, fixed_dds_path, material_compression_format)
                            else:
                                original_compression_format = get_compression_format_from_name(os.path.basename(image_path))
                                if original_compression_format:
                                    convert_to_dds(temp_png_path, fixed_dds_path, original_compression_format)
                                else:
                                    convert_to_dds(temp_png_path, fixed_dds_path, "BC3_UNORM")
                            node.image.filepath = bpy.path.relpath(fixed_dds_path)
                        else:
                            node.image.filepath = bpy.path.relpath(image_path)

        self.report({'INFO'}, "Mip Maps fixed.")
        return {'FINISHED'}

# Operator to fix mip maps for textures in a folder
class OBJECT_OT_FixFolderMipMaps(bpy.types.Operator):
    bl_idname = "object.fix_folder_mip_maps"
    bl_label = "Fix Folder Mip Maps"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_folder = context.scene.selected_folder

        if selected_folder:
            fixed_dds_folder = os.path.join(selected_folder, "Fixed_DDS")
            if not os.path.exists(fixed_dds_folder):
                os.makedirs(fixed_dds_folder)

            for file_name in os.listdir(selected_folder):
                file_path = os.path.join(selected_folder, file_name)
                if os.path.isfile(file_path) and file_name.lower().endswith('.dds'):
                    fixed_dds_path = os.path.join(fixed_dds_folder, file_name)
                    temp_png_path = os.path.splitext(file_path)[0] + ".png"
                    convert_to_png(file_path, temp_png_path)
                    
                    material_name = os.path.splitext(file_name)[0]
                    material_compression_format = get_compression_format_from_name(material_name)
                    
                    if material_compression_format:
                        convert_to_dds(temp_png_path, fixed_dds_path, material_compression_format)
                    else:
                        original_compression_format = get_compression_format_from_name(file_name)
                        if original_compression_format:
                            convert_to_dds(temp_png_path, fixed_dds_path, original_compression_format)
                        else:
                            convert_to_dds(temp_png_path, fixed_dds_path, "BC3_UNORM")
                            
                    os.remove(temp_png_path)

            self.report({'INFO'}, "Folder mip maps fixed.")
        else:
            self.report({'ERROR'}, "No folder selected.")

        return {'FINISHED'}

# Register classes
def register():
    bpy.utils.register_class(ConvertToDDSPanel)
    bpy.utils.register_class(OBJECT_OT_ConvertToDDS)
    bpy.utils.register_class(OBJECT_OT_FixMipMaps)
    bpy.utils.register_class(OBJECT_OT_FixFolderMipMaps)
    bpy.types.Scene.compression_format = bpy.props.EnumProperty(
        items=[
            ("BC1_UNORM", "BC1_UNORM (DXT1)", ""),
            ("BC2_UNORM", "BC2_UNORM (DXT3)", ""),
            ("BC3_UNORM", "BC3_UNORM (DXT5)", ""),
            ("BC4_UNORM", "BC4_UNORM (ATI1)", ""),
            ("BC5_UNORM", "BC5_UNORM (3Dc)", ""),
            ("BC6H_UF16", "BC6H_UF16", ""),
            ("BC7_UNORM", "BC7_UNORM", "")
        ],
        name="Compression Format",
        description="Compression format for DDS conversion"
    )
    bpy.types.Scene.selected_folder = bpy.props.StringProperty(name="Selected Folder", description="Selected folder for texture operations", subtype='DIR_PATH')

def unregister():
    bpy.utils.unregister_class(ConvertToDDSPanel)
    bpy.utils.unregister_class(OBJECT_OT_ConvertToDDS)
    bpy.utils.unregister_class(OBJECT_OT_FixMipMaps)
    bpy.utils.unregister_class(OBJECT_OT_FixFolderMipMaps)
    del bpy.types.Scene.compression_format
    del bpy.types.Scene.selected_folder

if __name__ == "__main__":
    register()
