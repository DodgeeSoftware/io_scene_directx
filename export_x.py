# ##### BEGIN ZLIB LICENSE BLOCK #####

# Copyright (c) <2020> <Dodgee Software>

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

# NOTE: Plugins need to through a pep8 checker. The following line
# sets the formatting requirements for this python file.
# <pep8 compliant>

import math
from math import radians
import mathutils
import bpy
from pathlib import Path

# TODO: Support for vertex colours via mesh.vertex_colors
# TODO: Do I need to figure out how to do parented meshes (nested transforms)

def ExportFile(filepath):
	bpy.ops.object.mode_set(mode="OBJECT")
	
	# Send a message to the console
	print("Exporting File: " + filepath)
	# Open the file for export
	f = open(filepath, "w", encoding="utf8", newline="\n")
	# Write the File Header to the file
	WriteHeader(f)
	# Write all the Template Boiler plate to the file
	WriteBoilerPlate(f)	
	# Go through all the objects in the scene
	for object in bpy.data.objects:
		# If the object type isn't a mesh then goto the next object
		if object.type != 'MESH':
			continue
		# Grab the Mesh from the Object
		mesh = object.data
		# Write the Object Name
		f.write("# " + object.name + "\n")
		f.write("Frame\n")
		f.write("{\n")
		# Write the FrameTransformationMatrix
		f.write("FrameTransformMatrix\n")
		f.write("{\n")
		# TODO: Try and replace this with a reusable function
		# Translation Matrix
		translationMatrix = mathutils.Matrix.Translation((object.location[0], object.location[2], object.location[1]))
		# Rotation about the X Axis Matrix
		#rotationXMatrix = mathutils.Matrix.Rotation((object.rotation_euler[0]), 4, 'X')
		rotationXMatrix = mathutils.Matrix.Identity(4)
		rotationXMatrix[1][1] = math.cos(-object.rotation_euler[0])
		rotationXMatrix[1][2] = -math.sin(-object.rotation_euler[0])
		rotationXMatrix[2][1] = math.sin(-object.rotation_euler[0])
		rotationXMatrix[2][2] = math.cos(-object.rotation_euler[0])
		# Rotation about the Y Axis Matrix
		#rotationYMatrix = mathutils.Matrix.Rotation((object.rotation_euler[2]), 4, 'Y')
		rotationYMatrix = mathutils.Matrix.Identity(4)
		rotationYMatrix[0][0] = math.cos(-object.rotation_euler[2])
		rotationYMatrix[0][2] = math.sin(-object.rotation_euler[2])
		rotationYMatrix[2][0] = -math.sin(-object.rotation_euler[2])
		rotationYMatrix[2][2] = math.cos(-object.rotation_euler[2])
		# Rotation about the Z Axis Matrix
		#rotationZMatrix = mathutils.Matrix.Rotation((object.rotation_euler[1]), 4, 'Z')
		rotationZMatrix = mathutils.Matrix.Identity(4)
		rotationZMatrix[0][0] = math.cos(-object.rotation_euler[1])
		rotationZMatrix[0][1] = -math.sin(-object.rotation_euler[1])
		rotationZMatrix[1][0] = math.sin(-object.rotation_euler[1])
		rotationZMatrix[1][1] = math.cos(-object.rotation_euler[1])
		# Scale Matrix
		scaleXMatrix = mathutils.Matrix.Scale(object.scale[0], 4, (1.0, 0.0, 0.0))
		scaleYMatrix = mathutils.Matrix.Scale(object.scale[2], 4, (0.0, 1.0, 0.0))
		scaleZMatrix = mathutils.Matrix.Scale(object.scale[1], 4, (0.0, 0.0, 1.0))
		# Compute the final Model transformation matrix
		finalMatrix = mathutils.Matrix(translationMatrix @ rotationYMatrix @ rotationZMatrix @ rotationXMatrix @scaleYMatrix @ scaleZMatrix @ scaleXMatrix)
		# Compute the matrix to transform the normals
		normalMatrix = mathutils.Matrix(rotationYMatrix @ rotationZMatrix @ rotationXMatrix)
		# The DirectX format stores  matrices 
		# in row major format so we transpose the
		# matrix here before writing
		finalMatrix.transpose()
		# Write the Matrix
		for j in range(0, 4):
			for i in range(0, 4):
				f.write(str('%.6f' % finalMatrix[j][i]))
				if j == 3 and i == 3:
					f.write(";;")
				else:
					f.write(",")
			f.write("\n")
		f.write("}\n")
		# Write the Mesh
		f.write("Mesh " + mesh.name + "\n{" + "\n")
		# Grab the Number of Vertices
		mesh_verts = mesh.vertices[:]
		# Grab the Number of Polygons
		mesh_polygons = mesh.polygons[:]
		# Count the Number of vertices
		vertexCount = 0
		for polygon in mesh_polygons:
			for vertex in polygon.vertices:
				vertexCount = vertexCount + 1
		# Write the Vertex Count
		f.write(str(vertexCount) + ";\n")
		# Go through all the polygons in the mesh
		subscriptOffset = 0
		for polygon in mesh_polygons:
			# Go through all the vertices in the polygon
			for i in range(len(polygon.vertices)):
				# Grab the vertex
				vertex = mesh_verts[polygon.vertices[i]]
				# Here I swap the Y and Z Axis
				f.write(str('%.6f' % vertex.co[0]) + ";" + str('%.6f' % vertex.co[2]) + ";" + str('%.6f' % (vertex.co[1])))
				# if we are at the last polygon and vertex write a double semicolon
				if polygon == mesh_polygons[-1] and i == (len(polygon.vertices) - 1):
					f.write(str(len(mesh_verts)) + ";;\n")
				else:
					f.write(str(len(mesh_verts)) + ";,\n")
			# Increment our subscripts
			subscriptOffset += len(polygon.vertices)
		f.write("\n")

		# Write the Number of Polygons
		f.write(str(len(mesh_polygons)) +";\n")
		# Write the Polygons
		subscriptOffset = 0
		for polygon in mesh_polygons:
			f.write(str(len(polygon.vertices)) + ";")
			for index in range(0, len(polygon.vertices)):
				indice = (subscriptOffset + (len(polygon.vertices) - 1) - index)
				f.write(str(indice))
				if index == len(polygon.vertices) - 1:
					f.write(";")
				else:
					f.write(",")
			if polygon == mesh_polygons[-1]:
				f.write(";")
			else:
				f.write(",")
			subscriptOffset = subscriptOffset + len(polygon.vertices)
			f.write("\n")
		f.write("\n")

		# TODO: Need to figure out how to provide support for per face vertex normals.
		# there must be away to create them in blender then detect them in script
		# and save them here when they exist. At the moment all polygons in a mesh
		# are hard edges and this is wrong
		# NOTE: We do NOT need to transform the normals.
		# It seems that the frametransform is applied automatically
		# to the normals
		f.write("MeshNormals \n{\n")
		# Calculate the Number of normals
		numNormals = 0
		for polygon in mesh_polygons:
			for vertex in polygon.vertices:
				numNormals = numNormals + 1
		# Write the Number of normals
		f.write(str(numNormals) + ";\n")
		for polygon in mesh_polygons:
			for vertex in polygon.vertices:
				if mesh.use_auto_smooth == False:
					normal = polygon.normal
				else:
					normal = mesh.vertices[vertex].normal
					#normal = polygon.normal
				f.write(str('%.6f' % normal.x) + ";")
				f.write(str('%.6f' % normal.z) + ";")
				f.write(str('%.6f' % normal.y) + ";")
				if polygon == mesh_polygons[-1]:
					if vertex == polygon.vertices[-1]:
						f.write(";")
					else:
						f.write(",")
				else:
					f.write(",")
				f.write("\n")
		f.write("\n")
		# Write the Number of Polygons
		f.write(str(len(mesh_polygons)) +";\n")
		# Write the Polygons
		subscriptOffset = 0
		for polygon in mesh_polygons:
			f.write(str(len(polygon.vertices)) + ";")
			for index in range(0, len(polygon.vertices)):
				indice = (subscriptOffset + (len(polygon.vertices) - 1) - index)
				f.write(str(indice))
				if index == len(polygon.vertices) - 1:
					f.write(";")
				else:
					f.write(",")
			if polygon == mesh_polygons[-1]:
				f.write(";")
			else:
				f.write(",")
			subscriptOffset = subscriptOffset + len(polygon.vertices)
			f.write("\n")
		f.write("}\n")

		# Do we have uv data?
		if len(mesh.uv_layers) > 0:
			# NOTE: There can only be one active UVMap per mesh. This
			# is set by the user in the interface.
			uvs = mesh.uv_layers.active.data[:]
			# Write the Name of the UVMap
			f.write("# " + str(mesh.uv_layers.active.name) + "\n")
			f.write("MeshTextureCoords \n{\n")
			# Write the UV coords for faces
			f.write(str(len(mesh.uv_layers.active.data[:])) + ";\n")
			# Write the UVs for each face
			subscriptOffset = 0
			for polygon in mesh_polygons:
				for index in range(0, len(polygon.vertices)):
					indice = (subscriptOffset + index)
					meshUVLoop = mesh.uv_layers.active.data[indice]
					f.write(str('%.6f' % meshUVLoop.uv[0]))
					f.write(";")
					f.write(str('%.6f' % (1.0 - meshUVLoop.uv[1])))
					f.write(";")
					if polygon == mesh_polygons[-1] and index == len(polygon.vertices) - 1:
						f.write(";")
					else:
						f.write(",")
					f.write("\n")
				subscriptOffset = subscriptOffset + len(polygon.vertices)
			f.write("}\n")

		# Grab the Materials used by this mesh
		mesh_materials = mesh.materials[:]		
		# Write the MeshMaterial List
		f.write("MeshMaterialList\n{\n")
		# Write the number of materials used by this mesh
		f.write(str(len(mesh_materials)) + ";\n")
		f.write(str(len(mesh_polygons)) +";\n")
		for index in range(0, len(mesh_polygons), 1):
			if index == len(mesh_polygons) - 1:
				f.write(str(mesh_polygons[index].material_index) +";\n")
			else:
				f.write(str(mesh_polygons[index].material_index) +",\n")

		for material in mesh_materials:
			f.write("Material "+ material.name + "\n{\n")
			if material.use_nodes == False:
				f.write("# This material doesn't use nodes. Doing best to export properties anyway. \n")
				# Write Diffuse Colour
				f.write(str('%.6f' % material.diffuse_color[0]) + ";" + str('%.6f' % material.diffuse_color[1]) + ";" + str('%.6f' % material.diffuse_color[2]) + ";" + str('%.6f' % material.diffuse_color[3]) + ";;\n")
				# Write specular cooeffiencnt
				f.write(str('%.6f' % material.specular_intensity) + ";\n")
				# Non-node materials in Blender have no specular colour write a default one here (white)
				f.write(str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";;\n")
				# Non-node materials in Blender have no emissive colour write a default one here (black)
				f.write(str('%.6f' % 0.0) + ";" + str('%.6f' % 0.0) + ";" + str('%.6f' % 0.0) + ";;\n")
			else:
				f.write("# Exporter deliberately and only supports the Specular Material Node in the Shader Graph \n")
				#specularNode = node for node in material.node_tree.nodes if node.type == ""
				faceColor = [1.0, 1.0, 1.0, 1.0]
				power = 200.0
				specularColor = [1.0, 1.0, 1.0, 1.0]
				emissiveColor = [0.0, 0.0, 0.0, 1.0]
				filenameandpath = ""
				for node in material.node_tree.nodes:
					if node.type == 'EEVEE_SPECULAR':
						# Grab Diffuse colour
						colorSocket = node.inputs[0]
						faceColor[0] = colorSocket.default_value[0]
						faceColor[1] = colorSocket.default_value[1]
						faceColor[2] = colorSocket.default_value[2]
						faceColor[3] = colorSocket.default_value[3]
						colorSocket = node.inputs[1]
						# Grab Specular colour
						specularColor[0] = colorSocket.default_value[0]
						specularColor[1] = colorSocket.default_value[1]
						specularColor[2] = colorSocket.default_value[2]
						floatSocket = node.inputs[2]
						power = floatSocket.default_value
						colorSocket = node.inputs[3]
						# Grab Emissive colour
						emissiveColor[0] = colorSocket.default_value[0]
						emissiveColor[1] = colorSocket.default_value[1]
						emissiveColor[2] = colorSocket.default_value[2]
					# If there is a texture grab the filenameandpath
					if node.type == 'TEX_IMAGE':
						image = node.image
						if image != None:
							filenameandpath = image.filepath
				# Write the Diffuse Colour
				f.write(str('%.6f' % faceColor[0]) + ";" + str('%.6f' % faceColor[1]) + ";" + str('%.6f' % faceColor[2]) + ";" + str('%.6f' % faceColor[3]) + ";;\n")
				# Write the Specular Cooefficient
				f.write(str('%.6f' % power) + ";\n")
				# Write the Specular Colour
				f.write(str('%.6f' % specularColor[0]) + ";" + str('%.6f' % specularColor[1]) + ";" + str('%.6f' % specularColor[2]) + ";;\n")
				# Write the Emissive Colour
				f.write(str('%.6f' % emissiveColor[0]) + ";" + str('%.6f' % emissiveColor[1]) + ";" + str('%.6f' % emissiveColor[2]) + ";;\n")
			# If there is a texture write the TexutreFilename node to the file
			if len(filenameandpath):
				f.write("TextureFilename\n{\n")
				#TODO: extract the filename from the filenameandpath
				f.write("\"" + Path(filenameandpath).name + "\"" + ";\n")
				f.write("}\n")
			f.write("}\n")
		# If there are no materials then use a default one
		# the file format must define at least one material
		# being material 0
		if len(mesh_materials) == 0:
			# Create the default Material Node give it a name TODO: Cannot have spaces investigate valid names
			f.write("Material "+ "DefaultMaterial" + "\n{\n")
			# Write the Diffuse Colour
			f.write(str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";;\n")
			# Write the Specular Cooefficient
			f.write(str('%.6f' % 2.0) + ";\n")
			# Write the Specular Colour
			f.write(str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";" + str('%.6f' % 1.0) + ";;\n")
			# Write the Emissive Colour
			f.write(str('%.6f' % 0.0) + ";" + str('%.6f' % 0.0) + ";" + str('%.6f' % 0.0) + ";;\n")
			f.write("}\n")
		f.write("}" + "\n")
		
		# if there is an armature modifier then write 
		# skeletal data to the file
		if object.modifiers.find("Armature") is not -1:
			# Grab the Armature object from the armature modifier
			armature = object.modifiers["Armature"].object.data
			boneCount = len(armature.bones.items())
			# Write the XSkinMeshHeader to file
			f.write("XSkinMeshHeader\n")
			f.write("{\n")
			f.write(str(boneCount) + ";" + " #nMaxSkinWeightsPerVertex \n")
			f.write(str(boneCount) + ";" + " #nMaxSkinWeightsPerFace \n")
			f.write(str(boneCount) + ";" + " #nBones \n")
			f.write("}\n")
			
			for vertexGroup in object.vertex_groups:
				f.write("SkinWeights\n")
				f.write("{\n")
				# WARNING: VertexGroup name isn't the same as Bone Name its the name in the heirachy which can be changed
				# the name of the vertex group should never be different from the joint name
				f.write("\"" + vertexGroup.name  + "\"; # name of the bone \n");
				
				# Count the verts in this skin
				vertSkinCount = 0
				# Go through each polygon in the Mesh
				for polygon in mesh_polygons:
					# Go through all the vertices in the polygon
					for i in range(len(polygon.vertices)):
						try:
							vertexGroup.weight(polygon.vertices[i])
							vertSkinCount += 1
						except RuntimeError:
							# vertex is not in the group
							pass
				# Write the number of vertices in the skin
				f.write(str(vertSkinCount) + "; #verts in this skin \n")
				
				# Create a dictionary for the weights
				skinIndices = list()
				skinWeights = list()
				# Go through each polygon in the Mesh
				for polygon in mesh_polygons:
					# Go through all the vertices in the polygon
					for i in range(len(polygon.vertices)):
						try:
							skinWeights.append(vertexGroup.weight(polygon.vertices[i]))
							skinIndices.append(polygon.vertices[i])
						except RuntimeError:
							# vertex is not in the group
							pass
				
				f.write("# list of indices \n")
				for i in range(len(skinIndices)):
					f.write(str(skinIndices[i]))
					if i < len(skinIndices) - 1:
						f.write(",\n")
					else:
						f.write(";\n")
						
				f.write("# list of weights \n")
				for i in range(len(skinWeights)):
					f.write(str('%.6f' % skinWeights[i]))
					if i < len(skinWeights) - 1:
						f.write(",\n")
					else:
						f.write(";\n")
				
				f.write("# offset matrix \n")
				# From official Documentation: 
				# The matrix matrixOffset transforms the mesh vertices to the space of the bone.
				# When concatenated to the bone's transform, this provides the world space coordinates of the mesh as affected by the bone
				bone = armature.bones[vertexGroup.name]
				
				# 8888888888888888888888888888
				
				boneMatrix = bone.matrix_local
				boneMatrix = boneMatrix.inverted()
				boneMatrix = object.modifiers["Armature"].object.matrix_world.inverted() @ boneMatrix
				boneMatrix = object.matrix_world @ boneMatrix

				# Grab bone location rotation and scale
				boneLocation = [ boneMatrix[0][3], boneMatrix[1][3], boneMatrix[2][3] ]
				myQuaternion = boneMatrix.to_quaternion()
				myEuler = myQuaternion.to_euler()
				boneRotation = [ myEuler[0], myEuler[1], myEuler[2] ]
				boneScale = [ boneMatrix[0][0], boneMatrix[1][2], boneMatrix[2][1] ]
				# Create translation Matrix
				tMatrix = mathutils.Matrix.Translation((boneLocation[0], boneLocation[2], boneLocation[1]))
				# Rotation about the X Axis Matrix
				rXMatrix = mathutils.Matrix.Identity(4)
				rXMatrix[1][1] = math.cos(-boneRotation[0])
				rXMatrix[1][2] = -math.sin(-boneRotation[0])
				rXMatrix[2][1] = math.sin(-boneRotation[0])
				rXMatrix[2][2] = math.cos(-boneRotation[0])
				# Rotation about the Y Axis Matrix
				rYMatrix = mathutils.Matrix.Identity(4)
				rYMatrix[0][0] = math.cos(-boneRotation[2])
				rYMatrix[0][2] = math.sin(-boneRotation[2])
				rYMatrix[2][0] = -math.sin(-boneRotation[2])
				rYMatrix[2][2] = math.cos(-boneRotation[2])
				# Rotation about the Z Axis Matrix
				rZMatrix = mathutils.Matrix.Identity(4)
				rZMatrix[0][0] = math.cos(-boneRotation[1])
				rZMatrix[0][1] = -math.sin(-boneRotation[1])
				rZMatrix[1][0] = math.sin(-boneRotation[1])
				rZMatrix[1][1] = math.cos(-boneRotation[1])
				# Create the Scale Matrices
				sXMatrix = mathutils.Matrix.Scale(boneScale[0], 4, (1.0, 0.0, 0.0))
				sYMatrix = mathutils.Matrix.Scale(boneScale[2], 4, (0.0, 1.0, 0.0))
				sZMatrix = mathutils.Matrix.Scale(boneScale[1], 4, (0.0, 0.0, 1.0))
				# Compute the final Model transformation matrix
				fMatrix = mathutils.Matrix(tMatrix @ rYMatrix @ rZMatrix @ rXMatrix @sYMatrix @ sZMatrix @ sXMatrix)
				# Tranpose before writing
				fMatrix.transpose()
				# Write the matrix
				for j in range(0, 4):
					for i in range(0, 4):
						f.write(str('%.6f' % fMatrix[j][i]))
						if i == 3 and j == 3:
							f.write("; ")
						else:
							f.write(", ")
						if i == 3:
							f.write("\n")


				
				# 8888888888888888888888888888
				
				## Write the Matrix
				#for j in range(0, 4):
					#for i in range(0, 4):
						#f.write(str('%.6f' % boneMatrix[j][i]))
						#if j == 3 and i == 3:
							#f.write(";;")
						#else:
							#f.write(",")
					#f.write("\n")
				#f.write("\n")
				#f.write("1.000000, 0.000000, 0.000000, 0.000000,\n")
				#f.write("0.000000, 0.000000, 1.000000, 0.000000,\n")
				#f.write("0.000000, 1.000000, 0.000000, 0.000000,\n")
				#f.write("0.000000, 0.000000, 0.000000, 1.000000;;\n")
				f.write("}\n")
			
			# Go through all bones looking for root bones
			for rootBone in armature.bones:
				# if bone is a root bone
				if rootBone.parent is None:
					WriteBoneAndChildren(f, rootBone)
				
		f.write("}\n")
		f.write("}\n")
		f.write("\n")
		
		if object.modifiers.find("Armature") is not -1:
			# Grab the Scene
			scene = bpy.context.scene
			# Write some interesting information into the file
			f.write("# Total Frames: " + str(scene.frame_end - scene.frame_start + 1) + "\n")
			f.write("# FPS: " + str(bpy.context.scene.render.fps) + "\n")
			f.write("# FPS Base: " + str(bpy.context.scene.render.fps_base) + "\n")
			f.write("AnimationSet\n")
			f.write("{\n")
			# Cache the current frame so we can store it later
			cacheCurrentFrame = scene.frame_current
			# OLD CODE WAS (When confident remove it)
			## Grab the Armature
			#armature = object.modifiers["Armature"].object.data
			## Grab the Bones from the Armature
			#bones = armature.bones
			
			# Grab the name of the armature
			armatureName = object.modifiers["Armature"].object.name
			# Grab the armature
			armature = bpy.data.objects[armatureName]
			# Grab the Bones from the Armature
			bones = armature.pose.bones
			
			# Calculate frame count
			frameCount = (scene.frame_end - scene.frame_start) + 1
			# Go through the bones one by one
			for bone in bones:
				f.write("Animation\n")
				f.write("{\n")
				f.write("AnimationKey\n")
				f.write("{\n")
				# TODO: Need to reconstruct the matrix for each frame here
				# so that Y is up and that the rotations are correct. Since this happens
				# a fair bit we need a function for it
				f.write("4; # keytype (4 is matrix type) \n")
				f.write(str(frameCount) +";" + "# numberofkeys\n")
				# Go through the scene one frame at a time scrubbing through the timeline
				for frame in range(scene.frame_start, scene.frame_end + 1, 1):
					# Set the frame for the animation
					scene.frame_set(frame)
					# Grab bone location rotation and scale
					boneLocation = bone.location
					boneRotation = bone.rotation_euler
					boneScale = bone.scale
					tMatrix = mathutils.Matrix.Translation((boneLocation[0], boneLocation[2], boneLocation[1]))
					# Rotation about the X Axis Matrix
					rXMatrix = mathutils.Matrix.Identity(4)
					rXMatrix[1][1] = math.cos(-boneRotation[0])
					rXMatrix[1][2] = -math.sin(-boneRotation[0])
					rXMatrix[2][1] = math.sin(-boneRotation[0])
					rXMatrix[2][2] = math.cos(-boneRotation[0])
					# Rotation about the Y Axis Matrix
					rYMatrix = mathutils.Matrix.Identity(4)
					rYMatrix[0][0] = math.cos(-boneRotation[2])
					rYMatrix[0][2] = math.sin(-boneRotation[2])
					rYMatrix[2][0] = -math.sin(-boneRotation[2])
					rYMatrix[2][2] = math.cos(-boneRotation[2])
					# Rotation about the Z Axis Matrix
					rZMatrix = mathutils.Matrix.Identity(4)
					rZMatrix[0][0] = math.cos(-boneRotation[1])
					rZMatrix[0][1] = -math.sin(-boneRotation[1])
					rZMatrix[1][0] = math.sin(-boneRotation[1])
					rZMatrix[1][1] = math.cos(-boneRotation[1])
					# Calculate Scale
					sXMatrix = mathutils.Matrix.Scale(boneScale[0], 4, (1.0, 0.0, 0.0))
					sYMatrix = mathutils.Matrix.Scale(boneScale[2], 4, (0.0, 1.0, 0.0))
					sZMatrix = mathutils.Matrix.Scale(boneScale[1], 4, (0.0, 0.0, 1.0))
					# Compute the final Model transformation matrix
					boneMatrix = mathutils.Matrix(tMatrix @ rYMatrix @ rZMatrix @ rXMatrix @sYMatrix @ sZMatrix @ sXMatrix)
					# Tranpose before writing
					boneMatrix.transpose()
					# Write the FrameNumber, NumberOfelementsIn4x4Matrix(16) and then the elements in the matrix
					f.write(str(frame) + ";" + "16" + ";")
					f.write("\n")
					# Write the bone Matrix
					for j in range(0, 4):
						for i in range(0, 4):
							f.write(str('%.6f' % boneMatrix[j][i]))
							if j == 3 and i == 3:
								f.write(";;")
							else:
								f.write(",")
						f.write("\n")
					if frame < scene.frame_end:
						f.write(",")
					else:
						f.write(";")
					f.write("\n")
				f.write("}\n")
				f.write("{" + bone.name + "}\n")
				f.write("}\n")
			# Restore the current frame 
			scene.frame_set(cacheCurrentFrame)
			f.write("}\n")
		f.write("\n")
	# Close the file
	f.close()
	# Complete the Export
	return {'FINISHED'}

def WriteHeader(f):
	f.write("xof 0302txt 0032\n")
	#f.write("Header {1; 0; 1;}\n") # TODO: This really isn't necessary should we remove this?
	#f.write("\n")
	f.write("# Created by DodgeeSoftware's DirectX Model Exporter\n")
	f.write("# Website: www.dodgeesoftware.com\n")
	f.write("# Email: info@dodgeesoftware.com\n")
	f.write("\n")

def WriteBoilerPlate(f):
	f.write("template Header\n")
	f.write("{\n")
	f.write("    <3D82AB43-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    WORD major;\n")
	f.write("    WORD minor;\n")
	f.write("    DWORD flags;\n")
	f.write("}\n\n")
	
	f.write("template Vector\n")
	f.write("{\n")
	f.write("    <3D82AB5E-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    FLOAT x;\n")
	f.write("    FLOAT y;\n")
	f.write("    FLOAT z;\n")
	f.write("}\n\n")

	f.write("template Coords2d\n")
	f.write("{\n")
	f.write("    <F6F23F44-7686-11cf-8F52-0040333594A3>\n")
	f.write("    FLOAT u;\n")
	f.write("    FLOAT v;\n")
	f.write("}\n\n")

	f.write("template Matrix4x4\n")
	f.write("{\n")
	f.write("    <F6F23F45-7686-11cf-8F52-0040333594A3>\n")
	f.write("    array FLOAT matrix[16];\n")
	f.write("}\n\n")

	f.write("template ColorRGBA\n")
	f.write("{\n")
	f.write("    <35FF44E0-6C7C-11cf-8F52-0040333594A3>\n")
	f.write("    FLOAT red;\n")
	f.write("    FLOAT green;\n")
	f.write("    FLOAT blue;\n")
	f.write("    FLOAT alpha;\n")
	f.write("}\n\n")

	f.write("template ColorRGB\n")
	f.write("{\n")
	f.write("    <D3E16E81-7835-11cf-8F52-0040333594A3>\n")
	f.write("    FLOAT red;\n")
	f.write("    FLOAT green;\n")
	f.write("    FLOAT blue;\n")
	f.write("}\n\n")

	f.write("template TextureFilename\n")
	f.write("{\n")
	f.write("    <A42790E1-7810-11cf-8F52-0040333594A3>\n")
	f.write("    STRING filename;\n")
	f.write("}\n\n")

	f.write("template Material\n")
	f.write("{\n")
	f.write("    <3D82AB4D-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    ColorRGBA faceColor;\n")
	f.write("    FLOAT power;\n")
	f.write("    ColorRGB specularColor;\n")
	f.write("    ColorRGB emissiveColor;\n")
	f.write("    [...]\n")
	f.write("}\n\n")

	f.write("template MeshFace\n")
	f.write("{\n")
	f.write("    <3D82AB5F-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    DWORD nFaceVertexIndices;\n")
	f.write("    array DWORD faceVertexIndices[nFaceVertexIndices];\n")
	f.write("}\n\n")

	f.write("template MeshTextureCoords\n")
	f.write("{\n")
	f.write("    <F6F23F40-7686-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD nTextureCoords;\n")
	f.write("    array Coords2d textureCoords[nTextureCoords];\n")
	f.write("}\n\n")

	f.write("template MeshMaterialList\n")
	f.write("{\n")
	f.write("    <F6F23F42-7686-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD nMaterials;\n")
	f.write("    DWORD nFaceIndexes;\n")
	f.write("    array DWORD faceIndexes[nFaceIndexes];\n")
	f.write("    [Material]\n")
	f.write("}\n\n")

	f.write("template MeshNormals\n")
	f.write("{\n")
	f.write("    <F6F23F43-7686-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD nNormals;\n")
	f.write("    array Vector normals[nNormals];\n")
	f.write("    DWORD nFaceNormals;\n")
	f.write("    array MeshFace faceNormals[nFaceNormals];\n")
	f.write("}\n\n")

	f.write("template Mesh\n")
	f.write("{\n")
	f.write("    <3D82AB44-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    DWORD nVertices;\n")
	f.write("    array Vector vertices[nVertices];\n")
	f.write("    DWORD nFaces;\n")
	f.write("    array MeshFace faces[nFaces];\n")
	f.write("    [...]\n")
	f.write("}\n\n")

	f.write("template FrameTransformMatrix\n")
	f.write("{\n")
	f.write("    <F6F23F41-7686-11cf-8F52-0040333594A3>\n")
	f.write("    Matrix4x4 frameMatrix;\n")
	f.write("}\n\n")

	f.write("template Frame\n")
	f.write("{\n")
	f.write("    <3D82AB46-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    [...]\n")
	f.write("}\n\n")

	f.write("template FloatKeys\n")
	f.write("{\n")
	f.write("    <10DD46A9-775B-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD nValues;\n")
	f.write("    array FLOAT values[nValues];\n")
	f.write("}\n\n")

	f.write("template TimedFloatKeys\n")
	f.write("{\n")
	f.write("    <F406B180-7B3B-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD time;\n")
	f.write("    FloatKeys tfkeys;\n")
	f.write("}\n\n")

	f.write("template AnimationKey\n")
	f.write("{\n")
	f.write("    <10DD46A8-775B-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD keyType;\n")
	f.write("    DWORD nKeys;\n")
	f.write("    array TimedFloatKeys keys[nKeys];\n")
	f.write("}\n\n")

	f.write("template AnimationOptions\n")
	f.write("{\n")
	f.write("    <E2BF56C0-840F-11cf-8F52-0040333594A3>\n")
	f.write("    DWORD openclosed;\n")
	f.write("    DWORD positionquality;\n")
	f.write("}\n\n")

	f.write("template Animation\n")
	f.write("{\n")
	f.write("    <3D82AB4F-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    [...]\n")
	f.write("}\n\n")

	f.write("template AnimationSet\n")
	f.write("{\n")
	f.write("    <3D82AB50-62DA-11cf-AB39-0020AF71E433>\n")
	f.write("    [Animation]\n")
	f.write("}\n\n")

	f.write("template XSkinMeshHeader\n")
	f.write("{\n")
	f.write("    <3cf169ce-ff7c-44ab-93c0-f78f62d172e2>\n")
	f.write("    WORD nMaxSkinWeightsPerVertex;\n")
	f.write("    WORD nMaxSkinWeightsPerFace;\n")
	f.write("    WORD nBones;\n")
	f.write("}\n\n")

	f.write("template VertexDuplicationIndices\n")
	f.write("{\n")
	f.write("    <b8d65549-d7c9-4995-89cf-53a9a8b031e3>\n")
	f.write("    DWORD nIndices;\n")
	f.write("    DWORD nOriginalVertices;\n")
	f.write("    array DWORD indices[nIndices];\n")
	f.write("}\n\n")

	f.write("template SkinWeights\n")
	f.write("{\n")
	f.write("    <6f0d123b-bad2-4167-a0d0-80224f25fabb>\n")
	f.write("    STRING transformNodeName;\n")
	f.write("    DWORD nWeights;\n")
	f.write("    array DWORD vertexIndices[nWeights];\n")
	f.write("    array FLOAT weights[nWeights];\n")
	f.write("    Matrix4x4 matrixOffset;\n")
	f.write("}\n\n")


# *****************************************
# * FUNCTIONS WHICH WRITE A SINGLE OBJECT *
# *****************************************

def WriteBool(f, value):
	print("not implemented yet")

def WriteBool2D(f, value):
	print("not implemented yet")

def WriteInt(f, value):
	print("not implemented yet")

def WriteFloat(f, value):
	print("not implemented yet")

def WriteString(f, text):
	print("not implemented yet")

def WriteVector(f, vector):
	print("not implemented yet")

def WriteVertex(f, vertex):
	print("not implemented yet")
	
def WriteColourRGB(f, colour):
	print("not implemented yet")

def WriteColourRGBA(f, colour):
	print("not implemented yet")

def WriteColourIndexed(f, colour):
	print("not implemented yet")

def WriteMatrix4x4(f, matrix):
	print("not implemented yet")

def WriteQuaternion(f, quaternion):
	print("not implemented yet")

def WriteBone(f, bone):
	print("not implemented yet")

def WriteMeshFace(f, face):
	print("not implemented yet")

def WriteMeshTextureCoords(f, textureCoords):
	print("not implemented yet")

def WriteMeshMaterialList(f, materialList):
	print("not implemented yet")

def WriteMeshNormals(f, meshNormals):
	print("not implemented yet")

def WriteVertextColours(f, meshVertexColours):
	print("not implemented yet")

def WriteTextureFilename(f, textureFilename):
	print("not implemented yet")
	
def WriteMaterial(f, material):
	print("not implemented yet")

def WriteMesh(f, mesh):
	print("not implemented yet")

def WriteFrameTransformMatrix(f, frameTransformMatrix):
	print("not implemented yet")

def WriteFrame(f, frame):
	print("not implemented yet")

def WriteFloatKeys(f, floatKeys):
	print("not implemented yet")

def WriteTimedFloatKeys(f, timedFloatKeys):
	print("not implemented yet")

def WriteAnimationKey(f, animationKey):
	print("not implemented yet")

def WriteAnimationOptions(f, animationOptions):
	print("not implemented yet")

def WriteAnimation(f, animation):
	print("not implemented yet")

def WriteAnimationSet(f, animationSet):
	print("not implemented yet")

def WriteBoneAndChildren(f, bone):
	# write its frame node
	f.write("Frame " + bone.name + "\n")
	f.write("{\n")
	# write its transform
	f.write("FrameTransformMatrix\n")
	f.write("{\n")
	# Grab the Bone Matrix relative to its parent
	boneMatrix = bone.matrix_local
	# Grab bone location rotation and scale
	boneLocation = [ boneMatrix[0][3], boneMatrix[1][3], boneMatrix[2][3] ]
	myQuaternion = boneMatrix.to_quaternion()
	myEuler = myQuaternion.to_euler()
	boneRotation = [ myEuler[0], myEuler[1], myEuler[2] ] # [ 0.0, 0.0, 0.0 ]
	boneScale = [ boneMatrix[0][0], boneMatrix[1][2], boneMatrix[2][1] ]
	# Create translation Matrix
	tMatrix = mathutils.Matrix.Translation((boneLocation[0], boneLocation[2], boneLocation[1]))
	# Rotation about the X Axis Matrix
	rXMatrix = mathutils.Matrix.Identity(4)
	rXMatrix[1][1] = math.cos(-boneRotation[0])
	rXMatrix[1][2] = -math.sin(-boneRotation[0])
	rXMatrix[2][1] = math.sin(-boneRotation[0])
	rXMatrix[2][2] = math.cos(-boneRotation[0])
	# Rotation about the Y Axis Matrix
	rYMatrix = mathutils.Matrix.Identity(4)
	rYMatrix[0][0] = math.cos(-boneRotation[2])
	rYMatrix[0][2] = math.sin(-boneRotation[2])
	rYMatrix[2][0] = -math.sin(-boneRotation[2])
	rYMatrix[2][2] = math.cos(-boneRotation[2])
	# Rotation about the Z Axis Matrix
	rZMatrix = mathutils.Matrix.Identity(4)
	rZMatrix[0][0] = math.cos(-boneRotation[1])
	rZMatrix[0][1] = -math.sin(-boneRotation[1])
	rZMatrix[1][0] = math.sin(-boneRotation[1])
	rZMatrix[1][1] = math.cos(-boneRotation[1])
	# Create the Scale Matrices
	sXMatrix = mathutils.Matrix.Scale(boneScale[0], 4, (1.0, 0.0, 0.0))
	sYMatrix = mathutils.Matrix.Scale(boneScale[2], 4, (0.0, 1.0, 0.0))
	sZMatrix = mathutils.Matrix.Scale(boneScale[1], 4, (0.0, 0.0, 1.0))
	# Compute the final Model transformation matrix
	finalMatrix = mathutils.Matrix(tMatrix @ rYMatrix @ rZMatrix @ rXMatrix @sYMatrix @ sZMatrix @ sXMatrix)
	# Tranpose before writing
	finalMatrix.transpose()
	# Write the matrix
	for j in range(0, 4):
		for i in range(0, 4):
			f.write(str('%.6f' % finalMatrix[j][i]))
			if i == 3 and j == 3:
				f.write("; ")
			else:
				f.write(", ")
			if i == 3:
				f.write("\n")
	f.write("}\n")
	# Write the child bones
	for childBone in bone.children:
		WriteBoneAndChildren(f, childBone)
	f.write("}\n")

# TODO: Review this function, does this also convert righthand to left hand?
def ConvertMatrixToYAxisUp(matrix):
	# Decompose the Matrix into component parts
	location, rotation, scale = matrix.decompose() # TODO: decompose is inaccurate need a better method
	
	# Translation Matrix
	translationMatrix = mathutils.Matrix.Translation((location.x, location.z, location.y))
	# Rotation about the X Axis Matrix
	#rotationXMatrix = mathutils.Matrix.Rotation((object.rotation_euler[0]), 4, 'X')
	rotationXMatrix = mathutils.Matrix.Identity(4)
	rotationXMatrix[1][1] = math.cos(-rotation.x)
	rotationXMatrix[1][2] = -math.sin(-rotation.x)
	rotationXMatrix[2][1] = math.sin(-rotation.x)
	rotationXMatrix[2][2] = math.cos(-rotation.x)
	# Rotation about the Y Axis Matrix
	#rotationYMatrix = mathutils.Matrix.Rotation((object.rotation_euler[2]), 4, 'Y')
	rotationYMatrix = mathutils.Matrix.Identity(4)
	rotationYMatrix[0][0] = math.cos(-rotation.z)
	rotationYMatrix[0][2] = math.sin(-rotation.z)
	rotationYMatrix[2][0] = -math.sin(-rotation.z)
	rotationYMatrix[2][2] = math.cos(-rotation.z)
	# Rotation about the Z Axis Matrix
	#rotationZMatrix = mathutils.Matrix.Rotation((object.rotation_euler[1]), 4, 'Z')
	rotationZMatrix = mathutils.Matrix.Identity(4)
	rotationZMatrix[0][0] = math.cos(-rotation.y)
	rotationZMatrix[0][1] = -math.sin(-rotation.y)
	rotationZMatrix[1][0] = math.sin(-rotation.y)
	rotationZMatrix[1][1] = math.cos(-rotation.y)
	# Scale Matrix
	scaleXMatrix = mathutils.Matrix.Scale(scale.x, 4, (1.0, 0.0, 0.0))
	scaleYMatrix = mathutils.Matrix.Scale(scale.z, 4, (0.0, 1.0, 0.0))
	scaleZMatrix = mathutils.Matrix.Scale(scale.y, 4, (0.0, 0.0, 1.0))
	
	# Compute the final Model transformation matrix
	finalMatrix = mathutils.Matrix.Identity(4)
	finalMatrix = mathutils.Matrix(translationMatrix @ rotationYMatrix @ rotationZMatrix @ rotationXMatrix @scaleYMatrix @ scaleZMatrix @ scaleXMatrix)
	return finalMatrix