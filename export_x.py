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

# TODO: Support for vertex colours via mesh.vertex_colors
# TODO: Support for vertex UVs

def ExportFile(filepath):
	print("Exporting File " + filepath)
	
	f = open(filepath, "w", encoding="utf8", newline="\n")

	# Write the File Header to the file
	WriteHeader(f)
	# Write all the Template Boiler plate to the file
	WriteBoilerPlate(f)
	
	# Write a list of all meshes in the scene
	for mesh in bpy.data.meshes:
		f.write("Frame\n{\n")
		# TODO: Figure out how to get the object's world transform
		f.write("FrameTransformMatrix\n{\n")
		f.write("#TODO: Implement me\n")
		f.write("}\n")
		f.write("Mesh " + mesh.name + "\n{" + "\n")
		# Grab the Number of Vertices
		mesh_verts = mesh.vertices[:]
		# Grab the Number of Polygons
		mesh_polygons = mesh.polygons[:]
		# Write the Vertex Count
		f.write(str(len(mesh_verts)) + ";\n")
		# Write the Vertices in the mesh
		for i in range(len(mesh_verts)):
			# TODO: Do I need to apply the Mesh transform here?
			vert = mesh_verts[i]
			f.write(str(vert.co[0]) + ";" + str(vert.co[1]) + ";" + str(vert.co[2]))
			if i == (len(mesh_verts) - 1):
				f.write(str(len(mesh_verts)) + ";;\n")
			else:
				f.write(str(len(mesh_verts)) + ";,\n")
		f.write("\n")
		# Write the Number of Polygons
		f.write(str(len(mesh_polygons)) +";\n")
		for polygon in mesh_polygons:
			f.write("3;")
			f.write(str(polygon.vertices[0]) + ",")
			f.write(str(polygon.vertices[1]) + ",")
			f.write(str(polygon.vertices[2]) + ",")
			f.write(";")
			f.write("\n")
		f.write("\n")
		# TODO: Figure out how to apply the transforms to the normals
		f.write("MeshNormals \n{\n")
		for polygon in mesh_polygons:
			vert1Index = polygon.vertices[0];
			vert2Index = polygon.vertices[1];
			vert3Index = polygon.vertices[2];
			f.write(str(mesh.vertices[vert1Index].normal[0]) + ",")
			f.write(str(mesh.vertices[vert1Index].normal[1]) + ",")
			f.write(str(mesh.vertices[vert1Index].normal[2]) + ",")
			f.write("\n")
			f.write(str(mesh.vertices[vert2Index].normal[0]) + ",")
			f.write(str(mesh.vertices[vert2Index].normal[1]) + ",")
			f.write(str(mesh.vertices[vert2Index].normal[2]) + ",")
			f.write("\n")
			f.write(str(mesh.vertices[vert3Index].normal[0]) + ",")
			f.write(str(mesh.vertices[vert3Index].normal[1]) + ",")
			f.write(str(mesh.vertices[vert3Index].normal[2]) + ",")
			f.write("\n")
		f.write("}\n")
		
		# Do we have uv data?
		if len(mesh.uv_layers) > 0:
			# NOTE: There can only be one active UVMap per mesh. This
			# is set by the user in the interface.
			uvs = mesh.uv_layers.active;
			# Write the Name of the UVMap
			f.write("# " + str(uvs.name))
			f.write("MeshTextureCoords \n{\n")
			
			f.write("#TODO: Implement me\n")
			
			f.write("}\n")
		
		# Grab the Materials used by this mesh
		mesh_materials = mesh.materials[:]
		
		# Write the MeshMaterial List
		f.write("MeshMaterialList\n{\n")
		# Write the number of materials used by this mesh
		f.write(str(len(mesh_materials)) + ";\n")
		f.write(str(len(mesh_polygons)) +";\n")
		for polygon in mesh_polygons:
			f.write(str(polygon.material_index) +",\n")			
		for material in mesh_materials:
			f.write("Material "+ material.name + "\n{\n")
			if material.use_nodes == False:
				f.write("# Material doesn't use nodes doing best to export properties \n")
				f.write(str(material.diffuse_color[0]) + ";" + str(material.diffuse_color[1]) + ";" + str(material.diffuse_color[2]) + ";" + str(material.diffuse_color[3]) + ";\n");
				f.write(str(material.specular_intensity) + ";\n")
				# PROBLEM: Non- node materials in Blender have no specular colour
				#f.write(str(material.specular_color[0]) + ";" + str(material.specular_color[1]) + ";" + str(material.specular_color[2]) + ";" + str(material.specular_color[3]) + ";\n");
				f.write(str(1.0) + ";" + str(1.0) + ";" + str(1.0) + ";" + str(1.0) + ";\n");
				# PROBLEM: Non-node materials in Blender have no emissive colour
				#f.write(str(material.emissive_color[0]) + ";" + str(material.emissive_color[1]) + ";" + str(material.emissive_color[2]) + ";" + str(material.emissive_color[3]) + ";\n");
				f.write(str(0) + ";" + str(0) + ";" + str(0) + ";" + str(0) + ";\n");
			else:
				f.write("# Exporter deliberately and only supports the Specular Material Node in the Shader Graph \n")
				#specularNode = node for node in material.node_tree.nodes if node.type == ""
				faceColor = [1.0, 1.0, 1.0, 1.0]
				power = 200.0
				specularColor = [1.0, 1.0, 1.0, 1.0]
				emissiveColor = [0.0, 0.0, 0.0, 1.0]
				filename = ""
				for node in material.node_tree.nodes:
					if node.type == 'EEVEE_SPECULAR':
						colorSocket = node.inputs[0]
						faceColor[0] = colorSocket.default_value[0]
						faceColor[1] = colorSocket.default_value[1]
						faceColor[2] = colorSocket.default_value[2]
						faceColor[3] = colorSocket.default_value[3]
						colorSocket = node.inputs[1]
						specularColor[0] = colorSocket.default_value[0]
						specularColor[1] = colorSocket.default_value[1]
						specularColor[2] = colorSocket.default_value[2]
						specularColor[3] = colorSocket.default_value[3]
						floatSocket = node.inputs[2]
						power = floatSocket.default_value
						colorSocket = node.inputs[3]
						emissiveColor[0] = colorSocket.default_value[0]
						emissiveColor[1] = colorSocket.default_value[1]
						emissiveColor[2] = colorSocket.default_value[2]
						emissiveColor[3] = colorSocket.default_value[3]
					if node.type == 'TEX_IMAGE':
						image = node.image
						if image != None:
							filename = image.filepath
				f.write(str(faceColor[0]) + "," + str(faceColor[1]) + "," + str(faceColor[2]) + "," + str(faceColor[3]) + ";\n")
				f.write(str(power) + ";\n")
				f.write(str(specularColor[0]) + "," + str(specularColor[1]) + "," + str(specularColor[2]) + "," + str(specularColor[3]) + ";\n")
				f.write(str(emissiveColor[0]) + "," + str(emissiveColor[1]) + "," + str(emissiveColor[2]) + "," + str(emissiveColor[3]) + ";\n")
			if len(filename):
				f.write("TextureFilename\n{\n")
				f.write(filename + ";\n")
				f.write("}\n")
			f.write("}\n")
		f.write("}" + "\n")
		f.write("}" + "\n")
		f.write("}")
		f.write("\n")

	f.close()
	return {'FINISHED'}

def WriteHeader(f):
	f.write("xof 0302txt 0032\n")
	f.write("Header {1; 0; 1;}\n")
	f.write("\n")
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