# SPDX-FileCopyrightText: 2026 Blender Studio Tools Authors
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Sculpt Mask FaceSets Tools",
    "author": "Seaway Liu",
    'version': (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sculpt Mode",
    "description": "Sculpt Mask FaceSets support Tools",
    "warning": "",
    "location": "View3D",
    "category": "Sculpt",
}

import os
import bpy
import rna_keymap_ui
from bpy.types import Menu, Operator,Panel, UIList, AddonPreferences
from bl_ui.space_toolsystem_common import ToolSelectPanelHelper,ToolDef
from bpy.props import StringProperty, EnumProperty, BoolProperty

from bpy.app.handlers import persistent
from . import translation



# ============================================
# 语言管理函数
# ============================================

_current_language = 'en_US'  # 默认语言

def gettext(msg):
    """获取当前语言的翻译文本"""
    return translation.get_translation(_current_language, msg)


def update_language(lang_code):
    """更新当前语言并刷新UI"""
    global _current_language
    _current_language = lang_code
    _refresh_ui()


def get_current_language():
    """获取当前语言代码"""
    return _current_language


def get_current_language_name():
    """获取当前语言名称"""
    return "中文" if _current_language == 'zh_CN' else "English"


def _refresh_ui():
    """刷新所有UI区域"""
    try:
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
    except Exception as e:
        print(f"刷新UI时出错: {e}")


# 简写
_ = gettext



# 存储快捷键引用的全局变量
addon_keymaps = []

class SCULPT_OT_Capture_Key(Operator):
    """捕获按键操作符 - 点击后等待用户按下快捷键"""
    bl_idname = "sculpt_assistant.capture_key"
    bl_label = "Capture Key"
    bl_description = "Click then press any key combination to set shortcut"
    
    # 存储回调函数名称，用于返回时更新哪个属性
    target_property: StringProperty(default='pie_menu_key')
    
    # 临时存储捕获的按键组合
    captured_key: StringProperty(default='')
    captured_ctrl: BoolProperty(default=False)
    captured_shift: BoolProperty(default=False)
    captured_alt: BoolProperty(default=False)
    captured_oskey: BoolProperty(default=False)
    
    # 标记是否已捕获
    key_captured: BoolProperty(default=False)
    
    def modal(self, context, event):
        """模态循环 - 处理按键事件"""
        
        # 按ESC取消捕获
        if event.type == 'ESC' and event.value == 'PRESS':
            self.report({'INFO'}, "Key capture cancelled")
            context.area.header_text_set(None)
            return {'CANCELLED'}
        
        
        if event.value == 'PRESS':
            if event.type in {'LEFT_CTRL', 'RIGHT_CTRL', 'LEFT_SHIFT', 'RIGHT_SHIFT', 
                              'LEFT_ALT', 'RIGHT_ALT', 'OSKEY'}:
                return {'RUNNING_MODAL'}
            
            # 捕获按键信息
            self.captured_key = event.type
            self.captured_ctrl = event.ctrl
            self.captured_shift = event.shift
            self.captured_alt = event.alt
            self.captured_oskey = event.oskey
            self.key_captured = True
            
            # 显示捕获到的按键
            key_display = self.format_key_display()
            self.report({'INFO'}, f"Captured: {key_display}")
            context.area.header_text_set(None)
            
            # 更新偏好设置
            self.update_preferences(context)
            
            return {'FINISHED'}
        
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        """调用时进入模态状态"""
        # 检查是否有偏好设置
        prefs = context.preferences.addons.get(__package__)
        if not prefs:
            self.report({'ERROR'}, "Cannot access addon preferences")
            return {'CANCELLED'}
        
        # 设置提示信息
        context.area.header_text_set("Press any key combination (ESC to cancel)")
        
        # 添加模态处理器
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def format_key_display(self):
        """格式化按键显示"""
        if not self.captured_key:
            return "None"
        
        parts = []
        if self.captured_ctrl:
            parts.append("Ctrl")
        if self.captured_shift:
            parts.append("Shift")
        if self.captured_alt:
            parts.append("Alt")
        if self.captured_oskey:
            parts.append("Cmd/Win")
        
        parts.append(self.captured_key)
        return " + ".join(parts)
    
    def update_preferences(self, context):
        """更新偏好设置并重新注册快捷键"""
        prefs = context.preferences.addons.get(__package__)
        if not prefs:
            return
        
        prefs = prefs.preferences
        
        # 更新偏好设置属性
        setattr(prefs, self.target_property, self.captured_key)
        setattr(prefs, 'pie_menu_ctrl', self.captured_ctrl)
        setattr(prefs, 'pie_menu_shift', self.captured_shift)
        setattr(prefs, 'pie_menu_alt', self.captured_alt)
        setattr(prefs, 'pie_menu_oskey', self.captured_oskey)
        
        # 触发更新
        from . import update_keymap
        update_keymap(prefs, context)


def get_keymap_item_properties(prefs):
    """从偏好设置获取快捷键属性，如果没有偏好设置则返回默认值"""
    if prefs:
        return {
            'idname': 'wm.call_menu_pie',  
            'properties': {  
                'name': 'sculpt_Mask_support.piemenu'  
            },
            'type': prefs.pie_menu_key,
            'value': 'PRESS',
            'ctrl': prefs.pie_menu_ctrl,
            'shift': prefs.pie_menu_shift,
            'alt': prefs.pie_menu_alt,
            'oskey': prefs.pie_menu_oskey,
        }
    else:
        # 返回默认快捷键
        return {
            'idname': 'wm.call_menu_pie',  
            'properties': {
                'name': 'sculpt_Mask_support.piemenu'  
            },
            'type': 'ONE',
            'value': 'PRESS',
            'ctrl': False,
            'shift': False,
            'alt': False,
            'oskey': False,
        }

def unregister_keymap():
    """注销快捷键"""
    global addon_keymaps
    
    # 遍历并移除所有快捷键
    for km, kmi in addon_keymaps:
        try:
            if km and kmi:
                km.keymap_items.remove(kmi)
        except (ReferenceError, TypeError, AttributeError) as e:
            # 如果对象无效，尝试通过查找方式清理
            try:
                if km and hasattr(km, 'keymap_items'):
                    for item in km.keymap_items:
                        if hasattr(item, 'idname') and item.idname == 'sculpt_Mask_support.piemenu':
                            km.keymap_items.remove(item)
                            break
            except:
                pass
    
    addon_keymaps.clear()



### 注册快捷键
def register_keymap():

    global addon_keymaps
    
    # 先清除现有的快捷键
    unregister_keymap()
    
    # 获取偏好设置
    prefs = bpy.context.preferences.addons.get(__package__)
    if prefs:
        prefs = prefs.preferences
    else:
        prefs = None
    
    # 获取快捷键属性
    kmi_props = get_keymap_item_properties(prefs)    
    
    # 创建新的键位映射
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        print(f"找到keyconfig: {kc.name}")
        
        # 创建或获取键位映射
        km = kc.keymaps.new(
            name='Sculpt',
            space_type='EMPTY',
            region_type='WINDOW'
        )
        
        try:
            # 创建键位映射项
            kmi = km.keymap_items.new(
                idname=kmi_props['idname'], 
                type=kmi_props['type'],
                value=kmi_props['value'],
                ctrl=kmi_props['ctrl'],
                shift=kmi_props['shift'],
                alt=kmi_props['alt'],
                oskey=kmi_props['oskey']
            )
            
            # 设置饼菜单名称属性 - 这是关键！
            if 'properties' in kmi_props:
                for prop_name, prop_value in kmi_props['properties'].items():
                    setattr(kmi.properties, prop_name, prop_value)
            
            
            # 存储引用
            addon_keymaps.append((km, kmi))
            
        except Exception as e:
            print(f"✗ 快捷键注册失败: {e}")
            import traceback
            traceback.print_exc()


def update_keymap(self, context):
    """当偏好设置改变时更新快捷键"""
    # 只有在插件启用时才更新
    if context.preferences.addons.get(__package__):
        register_keymap()



##############################################################
#  Tools UI
##############################################################


class SCULPT_MASK_PIEMENU(Menu):
    bl_label = "Sculpt Mask&FaceSet PM"
    bl_idname = "sculpt_Mask_support.piemenu"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        
        scene = bpy.context.scene
        
        ob = bpy.context.active_object
        brush = context.tool_settings.sculpt.brush        
        wm = bpy.context.window_manager
        tool = bpy.context.workspace.tools.from_space_view3d_mode(context.mode)
        
        # preferences
        addon_prefs = context.preferences.addons[__package__].preferences
        current_language = addon_prefs.language
        

##############################################################   Pie Right       
        
        col = pie.column(align=True) 
        col.scale_x = 0.9

        row = col.row(align=True) 
        row.scale_y = 1.5 
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.line_project"),).name = 'builtin.line_project'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.mask_by_color"),).name = 'builtin.mask_by_color' 
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.mesh_filter"),).name = 'builtin.mesh_filter'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.cloth_filter"),).name = 'builtin.cloth_filter'
        col.separator()
        
        if tool.idname == "builtin.mesh_filter":
            propsmesh = tool.operator_properties("sculpt.mesh_filter")
            
        if tool.idname == "builtin.cloth_filter":
            propscloth = tool.operator_properties("sculpt.cloth_filter")
            
        if tool.idname == "builtin.mask_by_color":
            propscolor = tool.operator_properties("sculpt.mask_by_color")
            
        if tool.idname == "builtin.line_project":
            propsline = tool.operator_properties("sculpt.project_line_gesture")
        
#--------------------------------                     
        try:
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop(propsmesh, "type", expand=False ,text="")
            
            col.prop(propsmesh, "strength")
            row = col.row(align=True)
            row.prop(propsmesh, "deform_axis")
            
            row = col.row(align=True)
            row.prop(propsmesh, "orientation", expand=True)
            if propsmesh.type == 'SURFACE_SMOOTH':
                col.prop(propsmesh, "surface_smooth_shape_preservation", expand=False)
                col.prop(propsmesh, "surface_smooth_current_vertex", expand=False)
            elif propsmesh.type == 'SHARPEN':
                col.prop(propsmesh, "sharpen_smooth_ratio", expand=False)
                col.prop(propsmesh, "sharpen_intensify_detail_strength", expand=False)
                col.prop(propsmesh, "sharpen_curvature_smooth_iterations", expand=False)                  
        except:pass
    
#--------------------------------        
        try:
            row = col.row(align=True)
            row.scale_y = 1.3
            row.prop(propscloth, "type", expand=False,text="")
            col.prop(propscloth, "strength")
            row = col.row(align=True)
            row.prop(propscloth, "force_axis")
            row = col.row(align=True)
            row.prop(propscloth, "orientation", expand=True)
            col.prop(propscloth, "cloth_mass")
            col.prop(propscloth, "cloth_damping")
            row = col.row(align=True)
            row.prop(propscloth, "use_face_sets",text="FaceSet")
            row.prop(propscloth, "use_collisions",text="Collosions")       
        except:pass    
    
    
#--------------------------------       
        try:
            col.prop(propscolor, "threshold")
            row = col.row(align=True)
            row.prop(propscolor, "contiguous")
            row.prop(propscolor, "invert")
            col.prop(propscolor, "preserve_previous_mask")
        except:pass
    
#--------------------------------        
        try:
            col.prop(propsline, "use_limit_to_segment", expand=False)
        except:pass    

        col.separator()
        col1 = col.box().column()       
        col1.label(text=_("Mask:"),icon='NODE_SOCKET_MATERIAL')  
        
        row = col1.row(align=True) 
        row.scale_y = 1.5                
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.border_mask"),).name = 'builtin.box_mask'   
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.lasso_mask"),).name = 'builtin.lasso_mask'
        
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.line_mask"),).name = 'builtin.line_mask'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.polyline_mask"),).name = 'builtin.polyline_mask'        
     
        col1.prop(context.space_data.overlay, "sculpt_mode_mask_opacity",text="Show Mask",)



        if tool.idname == "builtin.box_mask":
            props1 = tool.operator_properties("paint.mask_box_gesture") 
        
        if tool.idname == "builtin.lasso_mask":
            props1 = tool.operator_properties("paint.mask_lasso_gesture") 
            
        if tool.idname == "builtin.line_mask":
            props1 = tool.operator_properties("paint.mask_line_gesture") 
            
        if tool.idname == "builtin.polyline_mask":
            props1 = tool.operator_properties("paint.mask_polyline_gesture") 
        
        
        try:
            row = col1.row(align=True) 
            row.scale_y = 1.3             
            row.prop(props1, "use_front_faces_only", text="Front face Only")
            
            if tool.idname == "builtin.lasso_mask":
                col1.prop(props1, "use_smooth_stroke", text="Stabilize Stroke")
                if props1.use_smooth_stroke == True:
                     col1.prop(props1, "smooth_stroke_radius", text="Radius", slider=True)
                     col1.prop(props1, "smooth_stroke_factor", text="Factor", slider=True)
            
            if tool.idname == "builtin.line_mask":
                col1.prop(props1, "use_limit_to_segment", expand=False) 
                           
        except:pass
    
        col.separator()
        col1 = col.box().column()        
        col1.label(text=_("Create Mask:"),icon='NODE_SOCKET_MATERIAL') 
        row = col1.row(align=True) 
        row.scale_y = 1.2
        row.operator("sculpt.mask_from_boundary", text=_("Boundary")).boundary_mode='MESH'
        row.operator("sculpt.mask_from_boundary", text=_("FaceSet Bonundary")).boundary_mode='FACE_SETS'
        
        row = col1.row(align=True) 
        row.scale_y = 1.2
        row.operator("mesh.selection_to_mask", text=_("Edit Sel"))
        row.operator("sculpt.mask_from_cavity", text=_("Cavity")).settings_source='OPERATOR'
        row.operator("sculpt.mask_by_color", text=_("Color"))
        
        
        col2 = col.box().column()
        row = col2.row(align=True)
        row.scale_y = 1.2
        row.operator("paint.mask_invert", text=_("Invert"),icon="IMAGE_ALPHA")
        row.operator("paint.mask_clear", text=_("Clear"),icon="CANCEL")

        row = col2.row(align=True)
        row.scale_y = 1.2
        row.operator("sculpt.mask_filter", text=_("Smooth")).filter_type='SMOOTH'
        row.operator("sculpt.mask_filter", text=_("Sharpen")).filter_type='SHARPEN'

        row = col2.row(align=True)
        row.scale_y = 1.2
        op=row.operator("sculpt.mask_filter", text=_("Contrast+"))
        op.filter_type='CONTRAST_INCREASE'
        op.auto_iteration_count=False
        op.iterations=1

        op=row.operator("sculpt.mask_filter", text=_("Contrast-"))
        op.filter_type='CONTRAST_DECREASE'
        op.auto_iteration_count=False
        op.iterations=1

        col2.separator()
        row = col2.row(align=True)
        row.scale_y = 1.2
        row.operator("sculpt.mask_filter", text=_("Grow")).filter_type='GROW'
        row.operator("sculpt.mask_filter", text=_("Shrink")).filter_type='SHRINK'

        row = col2.row(align=True)
        row.scale_y = 1.2
        op = row.operator("sculpt.expand", text=_("By Topo"))
        op.target='MASK'
        op.falloff_type='GEODESIC'
        op.invert=False
        op.use_mask_preserve=True
        op.use_auto_mask=False

        op = row.operator("sculpt.expand", text=_("By Normals"))
        op.target='MASK'
        op.falloff_type='NORMALS'
        op.invert=False
        op.use_mask_preserve=True

        col.separator()
        col1 = col.box().column()
        col1.label(text=_("Mask Hide Tools:"),icon='NODE_SOCKET_MATERIAL')
        row = col1.row(align=True) 
        row.scale_y = 1.5                
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.border_hide"),).name = 'builtin.box_hide'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.lasso_hide"),).name = 'builtin.lasso_hide'       
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.line_hide"),).name = 'builtin.line_hide'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.polyline_hide"),).name = 'builtin.polyline_hide'
        
        
        if tool.idname == "builtin.box_hide":
            props2 = tool.operator_properties("paint.hide_show")
        
        if tool.idname == "builtin.lasso_hide":
            props2 = tool.operator_properties("paint.hide_show_lasso_gesture")
            
        if tool.idname == "builtin.polyline_hide":
            props2 = tool.operator_properties("paint.hide_show_polyline_gesture")
        
        
        try:            
            row = col1.row(align=True) 
            row.scale_y = 1.5
            row.prop(props2, "area", expand=False, text="")
            
            if tool.idname == "builtin.lasso_hide":
                col1.prop(props2, "use_smooth_stroke", )#text="Stabilize Stroke"
                if props2.use_smooth_stroke == True:
                     col1.prop(props2, "smooth_stroke_radius", text="Radius", slider=True)
                     col1.prop(props2, "smooth_stroke_factor", text="Factor", slider=True)                            
        except:pass
    
    
        if tool.idname == "builtin.line_hide":
            props2 = tool.operator_properties("paint.hide_show_line_gesture")
            
            try:
                col1.prop(props2, "use_limit_to_segment", )#text="limit to segment"
            except:pass





##########################################################################   Pie left   
 
        col = pie.column(align=True)
        col.scale_x = 0.9
        
        col1 = col.box().column()
        col1.label(text=_("Face Sets:"),icon='NODE_SOCKET_GEOMETRY')
        row = col1.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("brush.sculpt.draw_face_sets"),).name = 'builtin_brush.draw_face_sets'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.face_set_edit"),).name = 'builtin.face_set_edit'
        
        
        row = col1.row(align=True)
        row.scale_y = 1.3
        row.operator("paint.hide_show_all", text=_("All"),icon = "HIDE_OFF").action='SHOW'
        row.operator("paint.visibility_invert", text=_("Vis Invert"))
        row.operator("sculpt.face_set_change_visibility", text=_("Change Vis")).mode='HIDE_ACTIVE'
        
        if tool.idname == "builtin.face_set_edit":
            props = tool.operator_properties("sculpt.face_set_edit")
            
            try: 
                col1.prop(props, "mode", expand=False,text="")
                col1.prop(props, "modify_hidden")
            except:pass                
        col.separator()
                
        row = col.row(align=True) 
        row.scale_y = 1.5 
               
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.border_face_set"),).name = 'builtin.box_face_set'   
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.lasso_face_set"),).name = 'builtin.lasso_face_set'        
        
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.line_face_set"),).name = 'builtin.line_face_set'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.polyline_face_set"),).name = 'builtin.polyline_face_set'
        col.prop(bpy.context.space_data.overlay, "sculpt_mode_face_sets_opacity", text="Show Face Sets")    

        
        if tool.idname == "builtin.box_face_set":
            props = tool.operator_properties("sculpt.face_set_box_gesture") 
        
        if tool.idname == "builtin.lasso_face_set":
            props = tool.operator_properties("sculpt.face_set_lasso_gesture") 
            
        if tool.idname == "builtin.line_face_set":
            props = tool.operator_properties("sculpt.face_set_line_gesture") 
            
        if tool.idname == "builtin.polyline_face_set":
            props = tool.operator_properties("sculpt.face_set_polyline_gesture") 
        
        
        try:
            row = col.row(align=True) 
            row.scale_y = 1.3             
            row.prop(props, "use_front_faces_only", text="Front face Only")
            
            if tool.idname == "builtin.lasso_face_set":
                col.prop(props, "use_smooth_stroke", text="Stabilize Stroke")
                if props.use_smooth_stroke == True:
                     col.prop(props, "smooth_stroke_radius", text="Radius", slider=True)
                     col.prop(props, "smooth_stroke_factor", text="Factor", slider=True)
            
            if tool.idname == "builtin.line_face_set":
                col.prop(props, "use_limit_to_segment", expand=False) 
                           
        except:pass
        col.separator()
        
        col2 = col.box().column()
        col2.label(text=_("Create FaceSet："),icon='NODE_SOCKET_GEOMETRY') 
        col2.scale_x = 0.85
        row = col2.row(align=True)
        row.scale_y = 1.3 
        row.operator("sculpt.face_sets_create", text=_("Visible")).mode='VISIBLE'
        row.operator("sculpt.face_sets_init", text=_("Loose")).mode='LOOSE_PARTS'
        row = col2.row(align=True)
        row.scale_y = 1.3 
        row.operator("sculpt.face_sets_create", text=_("Mask")).mode='MASKED'        
        row.operator("sculpt.face_sets_create", text=_("Edit Sel")).mode='SELECTION'
        row.operator("sculpt.face_sets_randomize_colors", text=_("Random col"))
        

        
        row = col2.row(align=True)
        row.scale_y = 1.3
        
        row.operator("sculpt.face_sets_init", text=_("FaceBound")).mode='FACE_SET_BOUNDARIES'
        row.operator("sculpt.face_sets_init", text=_("Seam")).mode='UV_SEAMS'
        row.operator("sculpt.face_sets_init", text=_("Normal")).mode='NORMALS'
        
        row = col2.row(align=True)
        row.scale_y = 1.3
        row.operator("sculpt.face_sets_init", text=_("Bevel Weight")).mode='BEVEL_WEIGHT'        
        row.operator("sculpt.face_sets_init", text=_("Crease")).mode='CREASES'
        row.operator("sculpt.face_sets_init", text=_("Sharp")).mode='SHARP_EDGES'
        
        
        col2.separator()
        
        row = col2.row(align=True) 
        row.scale_y = 1.2 
        row.operator("sculpt.face_set_edit", text=_("Fair Positions")).mode='FAIR_POSITIONS'
        row.operator("sculpt.face_set_edit", text=_("Fair Tangency")).mode='FAIR_TANGENCY'
        
        row = col2.row(align=True) 
        row.scale_y = 1.2 
        row.operator("sculpt.face_set_edit", text=_("Grow")).mode='GROW'
        row.operator("sculpt.face_set_edit", text=_("Shrink")).mode='SHRINK'
        
        row = col2.row(align=True) 
        row.scale_y = 1.2 
        op = row.operator("sculpt.expand", text=_("By Topo"))
        op.target='FACE_SETS'
        op.falloff_type='GEODESIC'       
        
        op = row.operator("sculpt.expand", text=_("By Normals"))
        op.target='FACE_SETS'
        op.falloff_type='NORMALS'
        
                    
        
        row = col2.row(align=True)  
        row.scale_y = 1.3
        row.operator("sculpt.face_set_extract", text=_("Select Copy to new objects"))
                
        col.separator()
        
        col1 = col.box().column()
        col1.label(text=_("Trim:"),icon='NODE_SOCKET_GEOMETRY') 
        row = col1.row(align=True)
        row.scale_y = 1.3
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.box_trim"),).name = 'builtin.box_trim'           
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.lasso_trim"),).name = 'builtin.lasso_trim' 
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.line_trim"),).name = 'builtin.line_trim' 
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.sculpt.polyline_trim"),).name = 'builtin.polyline_trim' 
        
        col.separator()

        if tool.idname == "builtin.box_trim":
            props = tool.operator_properties("sculpt.trim_box_gesture")
          
          
        if tool.idname == "builtin.polyline_trim":
            props = tool.operator_properties("sculpt.trim_polyline_gesture")
            
            
        if tool.idname == "builtin.lasso_trim":
            props = tool.operator_properties("sculpt.trim_lasso_gesture")
            
        
        if tool.idname == "builtin.line_trim":
            props = tool.operator_properties("sculpt.trim_line_gesture")
             
            
        try:
            row = col1.row(align=True)
            row.scale_y = 1.3
            row.prop(props, "trim_solver", expand=False,text="")
            
            if tool.idname == "builtin.line_trim":
                row.prop(props, "use_limit_to_segment", expand=False) 
            else:row.prop(props, "trim_mode", expand=False,text="")
                
            row = col1.row(align=True) 
            row.scale_y = 1.3
            row.prop(props, "trim_orientation", expand=False,text="")
            row.prop(props, "trim_extrude_mode", expand=False,text="")
            col.prop(props, "use_cursor_depth", expand=False)
            

        
        
            if tool.idname == "builtin.lasso_trim":
                props = tool.operator_properties("sculpt.trim_lasso_gesture")
            
                col.prop(props, "use_smooth_stroke", text="Stabilize Stroke")
                if props.use_smooth_stroke == True:
                    col.prop(props, "smooth_stroke_radius", text="Radius", slider=True)
                    col.prop(props, "smooth_stroke_factor", text="Factor", slider=True)
        except:pass
            

        col.separator()

        col1 = col.box().column()
        col1.label(text=_("Add Mesh:"),icon='NODE_SOCKET_GEOMETRY')
        row = col1.row(align=True)
        row.scale_y = 1.3
        row.operator("sculpt.trim_box_gesture", text="Box",).trim_mode='JOIN'
        row.operator("sculpt.trim_lasso_gesture", text="Lasso").trim_mode='JOIN'
        row.operator("sculpt.trim_polyline_gesture", text="Polyline").trim_mode='JOIN'
         


########################################################################## Pie  Down    
        col = pie.column(align=True)
        
#        col.scale_x = 1.05
        
        addon_prefs = context.preferences.addons[__package__].preferences
        current_language = addon_prefs.language
        
        if current_language == 'zh_CN':
            # 中文界面，设置不同的缩放
            col.scale_x = 1.1
        elif current_language == 'en_US':
            col.scale_x = 0.95
        else:  # AUTO
            # 自动模式下，根据Blender语言设置
            if context.preferences.view.language == 'zh_CN':
                col.scale_x = 1.1
            else:
                col.scale_x = 0.95
        
        col2 = col.box().column()
        col2.label(text=_("Mesh Filter:"),icon='NODE_SOCKET_OBJECT')    
        col2.scale_x = 0.85
        row = col2.row(align=True)
        op = row.operator("sculpt.mesh_filter", text=_("Smooth"))
        op.type='SMOOTH'
        op.strength=1
        
        op=row.operator("sculpt.mesh_filter", text=_("Sharpen"))
        op.type='SHARPEN'
        op.strength=0.1
        
        row = col2.row(align=True)
        op = row.operator("sculpt.mesh_filter", text=_("Surface Smooth"))
        op.type='SURFACE_SMOOTH'
        op.strength=1        
        row.operator("sculpt.mesh_filter", text=_("Inflate")).type='INFLATE'
        
        row = col2.row(align=True)
        op=row.operator("sculpt.mesh_filter", text=_("Relax"))
        op.type='RELAX'
        op.strength=1
        
        op=row.operator("sculpt.mesh_filter", text=_("Relax FaceSet"))
        op.type='RELAX_FACE_SETS'
        op.strength=1
        
        
        
        row = col2.row(align=True)
        op=row.operator("sculpt.mesh_filter", text=_("Enhance Details"))
        op.type='ENHANCE_DETAILS'
        op.strength=1
        col2.operator("sculpt.mesh_filter", text=_("Erase Displacement")).type='ERASE_DISPLACEMENT' 
        
        

        col2 = col.box().column()
        col2.label(text=_("Mask Extract:"),icon='NODE_SOCKET_OBJECT') 
        col2.scale_y = 1.2
        row = col2.row(align=True)
        row.operator("sculpt.paint_mask_extract", text=_("Extract"),icon='SNAP_FACE')
        props = row.operator("sculpt.paint_mask_slice", text=_("Slice"))
        props.fill_holes = False
        props.new_object = False
        
        row = col2.row(align=True)        
        props = row.operator("sculpt.paint_mask_slice", text=_("Fill Holes"))
        props.new_object = False
        props = row.operator("sculpt.paint_mask_slice", text=_("to New Obj"))
        props.fill_holes = False
        props.new_object = True

         
          
     
         
         
         
         
         
##########################################################################  Pie up    
        col = pie.column(align=True) 
        col.scale_x = 0.75  
        
        
        colx = col.box().column()                
        row = colx.row(align=True)         
        colx.scale_y = 1.3
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.transform.transform"),).name = 'builtin.transform'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.transform.translate"),).name = 'builtin.move'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.transform.rotate"),).name = 'builtin.rotate'
        row.operator("wm.tool_set_by_id",text=" ",icon_value=ToolSelectPanelHelper._icon_value_from_icon_handle("ops.transform.resize"),).name = 'builtin.scale'
        
        
        row = colx.row(align=True)
        if tool.idname == "builtin.transform" or tool.idname == "builtin.move" or tool.idname == "builtin.rotate" or tool.idname == "builtin.scale":
            row.prop(scene.tool_settings.sculpt,"transform_mode",text="",)
        
        if tool.idname == "builtin.transform":
            row.prop(scene.transform_orientation_slots[1],"type",text="",)
        if tool.idname == "builtin.move":
            row.prop(scene.transform_orientation_slots[1],"type",text="",)
        if tool.idname == "builtin.rotate":
            row.prop(scene.transform_orientation_slots[2],"type",text="",)
        if tool.idname == "builtin.scale":
            row.prop(scene.transform_orientation_slots[3],"type",text="",)
        
        
        
        row = colx.row(align=True)
        row.operator("sculpt.set_pivot_position", text="Act").mode='ACTIVE'
        row.operator("sculpt.set_pivot_position", text="Sur").mode='SURFACE' 
        row.operator("sculpt.set_pivot_position", text="O").mode='ORIGIN'
        row.operator("sculpt.set_pivot_position", text="B").mode='BORDER'
        row.operator("sculpt.set_pivot_position", text="UM").mode='UNMASKED'            
         
        
        col2 = col.box().column()
        row = col2.row(align=True) 
        row.scale_y = 1.2 
        row.operator("paint.hide_show_all",text=_("All"),icon='HIDE_OFF').action='SHOW'
        row.operator("paint.hide_show_masked",text=_("Hide")).action='HIDE'
        row.operator("paint.visibility_invert",text=_("VisInvert"))   
        
        row = col2.row(align=True) 
        row.scale_y = 1.3  
        row.operator("paint.visibility_filter",text=_("Grow",)).action='GROW'
        row.operator("paint.visibility_filter",text=_("Shrink",)).action='SHRINK'
         
         
         
         
           
############################################################### 
#  Operator Code
###############################################################   
              


###############################################################
# AddonPreferences
############################################################### 
 
class My_AddonPreferences(AddonPreferences):
    bl_idname = __package__
       
    # 语言选择属性
    language: bpy.props.EnumProperty(
        name="Language",
        description="Select interface language",
        items=[
            ('AUTO', "Auto", "Use Blender's language setting"),
            ('en_US', "English", "English interface"),
            ('zh_CN', "中文", "中文界面"),
        ],
        default='AUTO',
        update=lambda self, context: update_language(self.language)
    )
    
    
    # 使用 StringProperty 存储按键代码
    pie_menu_key: StringProperty(
        name="Pie Menu Key",
        description="Key code for the pie menu",
        default='ONE',
        update=update_keymap
    )
    
    pie_menu_ctrl: BoolProperty(
        name="Ctrl",
        description="Require Ctrl key",
        default=False,
        update=update_keymap
    )
    
    pie_menu_shift: BoolProperty(
        name="Shift",
        description="Require Shift key",
        default=False,
        update=update_keymap
    )
    
    pie_menu_alt: BoolProperty(
        name="Alt",
        description="Require Alt key",
        default=False,
        update=update_keymap
    )
    
    pie_menu_oskey: BoolProperty(
        name="Cmd/Win",
        description="Require Cmd (Mac) or Win key",
        default=False,
        update=update_keymap
    )

    def draw(self, context):
        layout = self.layout
        
        
        # 语言选择
        box = layout.box()
        box.label(text=_("Select Language:"))
        row = box.row(align=True)
        row.prop(self, "language",expand=True)
        
        # 语言说明
        row = box.row(align=True)
        row.label(text=_("Current language: ") + get_current_language_name())
        
                
        box = layout.box()
        box.label(text=_("Customize Pie Menu Shortcut:"))
        row = box.row(align=True)  
        row.scale_y = 1.5
        # 当前快捷键显示
        current = self.get_current_key_display()
        row.label(text=_("Current Key:"), icon='KEYINGSET')
        row.label(text=current)

        capture_op = row.operator("sculpt_assistant.capture_key", text=_("Click set new shortcut"), icon='ADD')
        capture_op.target_property = 'pie_menu_key'
        
#        # 手动输入选项（作为备选）
#        box = col.box()
#        box.label(text="Or enter manually:", icon='PREFERENCES')
        
        
        # 修饰键
#        row = box.row()
#        row.label(text="",icon='PREFERENCES')
#        row.prop(self, "pie_menu_ctrl", text="Ctrl", toggle=1)
#        row.prop(self, "pie_menu_shift", text="Shift", toggle=1)
#        row.prop(self, "pie_menu_alt", text="Alt", toggle=1)
#        row.prop(self, "pie_menu_oskey", text="Cmd/Win", toggle=1)
        
        # 提示信息
#        col.separator()
        box = layout.box()
        info_col = box.column(align=True)
        info_col.label(text=_("How to set shortcut:"), icon='INFO')
        info_col.label(text=_("1. Click 'Click set new shortcut' button"))
        info_col.label(text=_("2. Press any key combination (Ctrl+Shift+A, etc.)"))
        info_col.label(text=_("Note: Changes will be saved automatically."))

    
    
    def get_current_key_display(self):
        """获取当前快捷键的显示文本"""
        parts = []
        if self.pie_menu_ctrl:
            parts.append("Ctrl")
        if self.pie_menu_shift:
            parts.append("Shift")
        if self.pie_menu_alt:
            parts.append("Alt")
        if self.pie_menu_oskey:
            parts.append("Cmd/Win")
        
        parts.append(self.pie_menu_key)
        return " + ".join(parts)       




# ============================================
# 语言处理程序
# ============================================

@persistent
def load_post_handler(dummy):
    """Blender完全启动后加载保存的语言设置"""
    try:
        addon_name = __package__
        if addon_name in bpy.context.preferences.addons:
            addon_prefs = bpy.context.preferences.addons[addon_name].preferences
            if hasattr(addon_prefs, 'language'):
                saved_language = addon_prefs.language
                update_language(saved_language)
    except Exception as e:
        update_language('en_US')  # 默认值



classes = [
    SCULPT_MASK_PIEMENU,
    My_AddonPreferences,
    SCULPT_OT_Capture_Key,
] #--End



def register():    
    for cls in classes:
        bpy.utils.register_class(cls)   
             
    register_keymap()
        
    #注册翻译到Blender系统
    bpy.app.translations.register(__name__, translation.get_all_translations())
    
    #添加翻译启动后处理程序
    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)
    
    #翻译-如果是重新加载插件，立即应用设置
    try:
        addon_name = __package__
        if addon_name in bpy.context.preferences.addons:
            addon_prefs = bpy.context.preferences.addons[addon_name].preferences
            if hasattr(addon_prefs, 'language'):
                update_language(addon_prefs.language)
    except:
        pass
    
    
    
def unregister():
    unregister_keymap()
    
    
    # 1. 移除翻译处理程序
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
    
    # 2. 注销翻译
    bpy.app.translations.unregister(__name__)
    
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    

if __name__ == "__main__":
    register()   
