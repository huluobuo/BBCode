# -*- coding: utf-8 -*-
"""导出 Blender logo.blend 模型为 JSON 格式"""

import bpy
import json
import os

# 清除默认场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 加载 blend 文件
bpy.ops.wm.open_mainfile(filepath='res/logo.blend')

# 提取模型数据
model_data = {
    'vertices': [],
    'faces': [],
    'normals': []
}

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        mesh = obj.data
        
        # 获取世界变换矩阵
        matrix_world = obj.matrix_world
        
        # 提取顶点
        for vert in mesh.vertices:
            # 应用世界变换
            co = matrix_world @ vert.co
            model_data['vertices'].append([co.x, co.y, co.z])
            
            # 提取法线
            normal = vert.normal
            model_data['normals'].append([normal.x, normal.y, normal.z])
        
        # 提取面（三角形索引）
        for poly in mesh.polygons:
            if len(poly.vertices) == 3:
                model_data['faces'].append([poly.vertices[0], poly.vertices[1], poly.vertices[2]])
            elif len(poly.vertices) == 4:
                # 四边形拆分为两个三角形
                model_data['faces'].append([poly.vertices[0], poly.vertices[1], poly.vertices[2]])
                model_data['faces'].append([poly.vertices[0], poly.vertices[2], poly.vertices[3]])

# 保存为 JSON
os.makedirs('res', exist_ok=True)
with open('res/logo_model.json', 'w') as f:
    json.dump(model_data, f)

print('模型导出成功！')
print(f'顶点数: {len(model_data["vertices"])}')
print(f'面数: {len(model_data["faces"])}')
