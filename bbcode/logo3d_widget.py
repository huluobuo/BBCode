# -*- coding: utf-8 -*-
"""
3D Logo 渲染组件 - 使用 PyQt6 + OpenGL 渲染 Blender 模型
"""

import json
import math
import random
import os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QPainterPath
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


class Logo3DWidget(QOpenGLWidget):
    """3D Logo 渲染组件 - 使用 OpenGL 渲染 Blender 模型"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        # 设置透明背景
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 旋转角度
        self._angle_z = 0  # Z轴旋转（主轴）
        self._angle_x = 0  # X轴偏移旋转
        self._angle_y = 0  # Y轴偏移旋转
        
        # 随机轨道偏移
        self._orbit_offset_x = random.uniform(-30, 30)
        self._orbit_offset_y = random.uniform(-30, 30)
        self._orbit_speed_x = random.uniform(0.3, 1.0)
        self._orbit_speed_y = random.uniform(0.3, 1.0)
        
        # 加载模型数据
        self._vertices = []
        self._faces = []
        self._normals = []
        self._load_model()
        
        # 计算模型边界框用于自动缩放
        self._calculate_bounds()
        
        # 动画定时器 - 使用更短的间隔提高流畅度
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_rotation)
        self._timer.start(16)  # 60fps，平衡流畅度和性能
    
    def _load_model(self):
        """从 JSON 文件加载 Blender 模型"""
        model_path = os.path.join(os.path.dirname(__file__), '..', 'res', 'logo_model.json')
        
        try:
            with open(model_path, 'r') as f:
                model_data = json.load(f)
            
            self._vertices = model_data.get('vertices', [])
            self._faces = model_data.get('faces', [])
            self._normals = model_data.get('normals', [])
            
            print(f"3D模型加载成功: {len(self._vertices)} 顶点, {len(self._faces)} 面")
        except Exception as e:
            print(f"加载3D模型失败: {e}")
            # 使用默认的简单立方体
            self._create_default_model()
    
    def _create_default_model(self):
        """创建默认的立方体模型（当加载失败时）"""
        # 简单的立方体顶点
        self._vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # 底面
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # 顶面
        ]
        
        # 立方体面（三角形）
        self._faces = [
            [0, 1, 2], [0, 2, 3],  # 底面
            [4, 7, 6], [4, 6, 5],  # 顶面
            [0, 4, 5], [0, 5, 1],  # 前面
            [2, 6, 7], [2, 7, 3],  # 后面
            [0, 3, 7], [0, 7, 4],  # 左面
            [1, 5, 6], [1, 6, 2]   # 右面
        ]
        
        # 默认法线
        self._normals = [[0, 0, 1]] * len(self._vertices)
    
    def _calculate_bounds(self):
        """计算模型边界框并确定缩放比例"""
        if not self._vertices:
            self._scale = 1.0
            self._center = [0, 0, 0]
            return
        
        # 计算边界框
        min_x = min(v[0] for v in self._vertices)
        max_x = max(v[0] for v in self._vertices)
        min_y = min(v[1] for v in self._vertices)
        max_y = max(v[1] for v in self._vertices)
        min_z = min(v[2] for v in self._vertices)
        max_z = max(v[2] for v in self._vertices)
        
        # 计算中心点
        self._center = [
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
            (min_z + max_z) / 2
        ]
        
        # 计算缩放比例（使模型适应窗口）
        size_x = max_x - min_x
        size_y = max_y - min_y
        size_z = max_z - min_z
        max_size = max(size_x, size_y, size_z)
        
        if max_size > 0:
            self._scale = 180.0 / max_size  # 缩放以适应 200x200 的窗口（放大3倍）
        else:
            self._scale = 1.0
    
    def _update_rotation(self):
        """更新旋转角度"""
        # Z轴主旋转 - 使用更小的增量配合更高的帧率
        self._angle_z = (self._angle_z + 0.5) % 360

        # 随机轨道偏移旋转 - 进一步减小增量
        self._angle_x = (self._angle_x + self._orbit_speed_x * 0.3) % 360
        self._angle_y = (self._angle_y + self._orbit_speed_y * 0.3) % 360

        self.update()
    
    def paintGL(self):
        """OpenGL 渲染"""
        import OpenGL.GL as gl

        # 清空背景 - 透明
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
        # 启用深度测试
        gl.glEnable(gl.GL_DEPTH_TEST)
        
        # 设置投影矩阵
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # 透视投影
        fov = 45.0
        aspect = self.width() / self.height()
        near = 0.1
        far = 1000.0
        
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        gl.glFrustum(-near * f * aspect, near * f * aspect, -near * f, near * f, near, far)
        
        # 设置模型视图矩阵
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # 相机位置
        gl.glTranslatef(0, 70, -180)  # 向上移动30，拉远相机
        
        # 应用轨道偏移
        offset_x = math.sin(math.radians(self._angle_x)) * self._orbit_offset_x * 0.05
        offset_y = math.cos(math.radians(self._angle_y)) * self._orbit_offset_y * 0.05
        gl.glTranslatef(offset_x, offset_y, 0)
        
        # 应用旋转 - 以 Z 轴为主轴
        # 先调整模型方向，让正面朝向观众
        gl.glRotatef(-90, 1, 0, 0)  # 绕X轴旋转-90度，让模型正面朝上
        gl.glRotatef(self._angle_z, 0, 0, 1)  # Z轴旋转（主轴）
        gl.glRotatef(self._angle_x * 0.3, 1, 0, 0)  # X轴随机偏移
        gl.glRotatef(self._angle_y * 0.3, 0, 1, 0)  # Y轴随机偏移
        
        # 绘制 3D 模型
        self._draw_model(gl)
    
    def _draw_model(self, gl):
        """绘制 3D 模型 - 无光照，使用纯色"""
        # 禁用光照，使用纯色渲染
        gl.glDisable(gl.GL_LIGHTING)
        
        # 设置颜色（绿色主题）
        gl.glColor3f(0.31, 0.9, 0.5)  # #4ec9b0 近似色
        
        # 绘制三角形面
        gl.glBegin(gl.GL_TRIANGLES)
        
        for face in self._faces:
            if len(face) >= 3:
                # 绘制三个顶点（应用缩放和中心偏移）
                for idx in [0, 1, 2]:
                    v = self._vertices[face[idx]]
                    x = (v[0] - self._center[0]) * self._scale
                    y = (v[1] - self._center[1]) * self._scale
                    z = (v[2] - self._center[2]) * self._scale
                    gl.glVertex3f(x, y, z)
        
        gl.glEnd()
        
        # 绘制线框（可选，增加轮廓感）
        gl.glColor3f(0.2, 0.7, 0.4)  # 稍深的绿色
        gl.glLineWidth(1.0)
        gl.glBegin(gl.GL_LINES)
        
        for face in self._faces:
            if len(face) >= 3:
                # 绘制三角形的边
                for i in range(3):
                    v1 = self._vertices[face[i]]
                    v2 = self._vertices[face[(i + 1) % 3]]
                    
                    x1 = (v1[0] - self._center[0]) * self._scale
                    y1 = (v1[1] - self._center[1]) * self._scale
                    z1 = (v1[2] - self._center[2]) * self._scale
                    
                    x2 = (v2[0] - self._center[0]) * self._scale
                    y2 = (v2[1] - self._center[1]) * self._scale
                    z2 = (v2[2] - self._center[2]) * self._scale
                    
                    gl.glVertex3f(x1, y1, z1)
                    gl.glVertex3f(x2, y2, z2)
        
        gl.glEnd()
    
    def _calculate_normal(self, v0, v1, v2):
        """计算三角形的法线"""
        # 向量 v0->v1 和 v0->v2
        a = [v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2]]
        b = [v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2]]
        
        # 叉积
        normal = [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ]
        
        # 归一化
        length = math.sqrt(sum(x**2 for x in normal))
        if length > 0:
            normal = [x / length for x in normal]
        
        return normal
    
    def stop_animation(self):
        """停止动画"""
        self._timer.stop()


# 备用方案：使用 QPainter 绘制伪3D效果
class Logo3DFallbackWidget(QWidget):
    """3D Logo 备用渲染组件 - 使用 QPainter 绘制"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        
        # 旋转角度
        self._angle_z = 0
        self._angle_x = 0
        self._angle_y = 0
        
        # 随机轨道偏移
        self._orbit_offset_x = random.uniform(-30, 30)
        self._orbit_offset_y = random.uniform(-30, 30)
        self._orbit_speed_x = random.uniform(0.3, 1.0)
        self._orbit_speed_y = random.uniform(0.3, 1.0)
        
        # 加载模型数据
        self._vertices = []
        self._faces = []
        self._load_model()
        
        # 动画定时器 - 使用更短的间隔提高流畅度
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_rotation)
        self._timer.start(16)  # 60fps
    
    def _load_model(self):
        """从 JSON 文件加载模型"""
        model_path = os.path.join(os.path.dirname(__file__), '..', 'res', 'logo_model.json')
        
        try:
            with open(model_path, 'r') as f:
                model_data = json.load(f)
            
            self._vertices = model_data.get('vertices', [])
            self._faces = model_data.get('faces', [])
            print(f"备用渲染器模型加载成功: {len(self._vertices)} 顶点")
        except Exception as e:
            print(f"备用渲染器加载模型失败: {e}")
            self._create_default_model()
    
    def _create_default_model(self):
        """创建默认模型"""
        self._vertices = [
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
        ]
        self._faces = [
            [0, 1, 2], [0, 2, 3], [4, 7, 6], [4, 6, 5],
            [0, 4, 5], [0, 5, 1], [2, 6, 7], [2, 7, 3],
            [0, 3, 7], [0, 7, 4], [1, 5, 6], [1, 6, 2]
        ]
    
    def _update_rotation(self):
        """更新旋转角度"""
        self._angle_z = (self._angle_z + 0.8) % 360
        self._angle_x = (self._angle_x + self._orbit_speed_x * 0.5) % 360
        self._angle_y = (self._angle_y + self._orbit_speed_y * 0.5) % 360
        self.update()
    
    def paintEvent(self, event):
        """绘制 3D 模型"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 清空背景 - 透明
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))
        
        # 计算中心点
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # 计算轨道偏移
        offset_x = math.sin(math.radians(self._angle_x)) * self._orbit_offset_x
        offset_y = math.cos(math.radians(self._angle_y)) * self._orbit_offset_y
        
        # 投影并绘制所有面
        projected_faces = []
        
        for face in self._faces:
            if len(face) >= 3:
                # 获取三个顶点
                v0 = self._vertices[face[0]]
                v1 = self._vertices[face[1]]
                v2 = self._vertices[face[2]]
                
                # 应用旋转变换
                rv0 = self._rotate_vertex(v0)
                rv1 = self._rotate_vertex(v1)
                rv2 = self._rotate_vertex(v2)
                
                # 透视投影
                p0 = self._project(rv0, center_x + offset_x, center_y + offset_y)
                p1 = self._project(rv1, center_x + offset_x, center_y + offset_y)
                p2 = self._project(rv2, center_x + offset_x, center_y + offset_y)
                
                # 计算平均深度用于排序
                avg_z = (rv0[2] + rv1[2] + rv2[2]) / 3
                
                # 计算法线用于背面剔除
                normal = self._calculate_normal_2d(p0, p1, p2)
                
                if normal > 0:  # 只绘制正面
                    projected_faces.append((avg_z, [p0, p1, p2]))
        
        # 按深度排序（远的先画）
        projected_faces.sort(key=lambda x: x[0], reverse=True)
        
        # 绘制面
        for depth, points in projected_faces:
            # 根据深度调整亮度
            brightness = int(100 + (depth + 2) * 30)
            brightness = max(60, min(180, brightness))
            
            color = QColor(78, 201, 176, brightness)
            painter.setBrush(color)
            painter.setPen(QPen(QColor(78, 201, 176), 1))
            
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()
            painter.drawPath(path)
    
    def _rotate_vertex(self, v):
        """对顶点应用旋转变换"""
        x, y, z = v

        # 缩放（放大3倍）
        scale = 75
        x *= scale
        y *= scale
        z *= scale

        # 先调整模型方向，让正面朝向观众
        # 绕X轴旋转-90度
        y_new = y
        z_new = -z
        y, z = y_new, z_new

        # Z轴旋转（主轴）
        rad_z = math.radians(self._angle_z)
        cos_z = math.cos(rad_z)
        sin_z = math.sin(rad_z)
        x_new = x * cos_z - y * sin_z
        y_new = x * sin_z + y * cos_z
        x, y = x_new, y_new
        
        # X轴旋转（随机偏移）
        rad_x = math.radians(self._angle_x * 0.3)
        cos_x = math.cos(rad_x)
        sin_x = math.sin(rad_x)
        y_new = y * cos_x - z * sin_x
        z_new = y * sin_x + z * cos_x
        y, z = y_new, z_new
        
        # Y轴旋转（随机偏移）
        rad_y = math.radians(self._angle_y * 0.3)
        cos_y = math.cos(rad_y)
        sin_y = math.sin(rad_y)
        x_new = x * cos_y + z * sin_y
        z_new = -x * sin_y + z * cos_y
        x, z = x_new, z_new
        
        return [x, y, z]
    
    def _project(self, v, cx, cy):
        """透视投影"""
        fov = 200
        distance = 5
        scale = fov / (distance - v[2] / 50)
        x = cx + v[0] * scale / 200
        y = cy - v[1] * scale / 200  # Y轴翻转
        return [x, y]
    
    def _calculate_normal_2d(self, p0, p1, p2):
        """计算2D三角形的法线（用于背面剔除）"""
        return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])
    
    def stop_animation(self):
        """停止动画"""
        self._timer.stop()
