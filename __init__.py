# ##### BEGIN ZLIB LICENSE BLOCK #####

# Copyright (c) <2019> <Dodgee Software>

# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1.  The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
# 2.  Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
# 3.  This notice may not be removed or altered from any source distribution.

# ##### END ZLIB LICENSE BLOCK #####

# NOTE: Plugins need to pass through a pep8 checker. The following line
# sets the formatting requirements for this python file.
# <pep8 compliant>

# The bl_info is a meta field used by Blender to describe this addon
bl_info = {
	"name": "DirectX X Format",
	"author": "Dodgee Software",
	"version": (0, 0, 1),
	"blender": (2, 80, 0),
	"location": "File > Export > DirectX (.x)",
	"description": "Export mesh vertices, UV's, materials, textures, "
				   "vertex colors, armatures, empties, and actions.",
	"wiki_url": "https://dodgeesoftware.com.au",
	"category": "Import-Export"}

from .import_x import *
from .export_x import *

import bpy
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.props import StringProperty
from bpy.props import (
		StringProperty,
		BoolProperty,
		FloatProperty,
		EnumProperty,
		)
from bpy_extras.io_utils import (
		ImportHelper,
		ExportHelper,
		orientation_helper,
		path_reference_mode,
		axis_conversion,
		)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportX(bpy.types.Operator, ImportHelper):
	"""Load a X file"""
	bl_idname = "import_scene.x"
	bl_label = "Import X"
	bl_options = {'UNDO', 'PRESET'}

	directory: StringProperty()

	filename_ext = ".x"
	filter_glob: StringProperty(default="*.x", options={'HIDDEN'})
	
	def draw(self, context):
		layout = self.layout

	def execute(self, context):
		return ImportFile(self.filepath)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportX(bpy.types.Operator, ExportHelper):
	"""Write a X file"""
	bl_idname = "export_scene.x"
	bl_label = "Export X"
	bl_options = {'UNDO', 'PRESET'}

	filename_ext = ".x"
	filter_glob: StringProperty(default="*.x", options={'HIDDEN'})
	
	def draw(self, context):
		layout = self.layout
	
	@property
	def check_extension(self):
		return True
	
	def execute(self, context):
		return ExportFile(self.filepath)

def menu_func_import(self, context):
	self.layout.operator(ImportX.bl_idname, text="DirectX X (.x)")

def menu_func_export(self, context):
	self.layout.operator(ExportX.bl_idname, text="DirectX X (.x)")

classes = (
	ExportX,
	ImportX
)

def register():
	print("Registering plugin: io_scene_directx")
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
	print("Deregistering plugin: io_scene_directx")
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
	register()
