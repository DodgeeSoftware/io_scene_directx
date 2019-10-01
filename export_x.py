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

import bpy

def ExportFile(filepath):
	print("Exporting File " + filepath)
	f = open(filepath,"w+")
	f.write("# Created by DodgeeSoftware's DirectX Model Exporter\n")
	f.write("# www.dodgeesoftware.com\n")
	f.write("\n")
	f.write("# This is the file header\n")
	f.write("xof 0302txt 0064\n")
	f.write("\n")
	f.write("# Template tags should go here\n")
	f.write("\n")
	f.write("# Model Data goes here inside tags\n")

	# Write a list of all object in the scene
	for obj in bpy.data.objects:
		f.write(obj.name + "\n")

	f.close()
	return {'FINISHED'}