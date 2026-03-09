# 翻译字典
TRANSLATIONS = {
    "en_US": {        
        ##### Pie界面 
        # Pie Right  
        "Boundary":"Boundary",
        "FaceSet Bonundary":"FaceSet Bonundary",
        "Edit Sel":"Edit Sel",
        "Cavity":"Cavity",
        "Color":"Color",        
        "Mask:": "Mask:",
        "Create Mask:":"Create Mask:",        
        "Invert":"Invert",
        "Clear":"Clear",
        "Smooth":"Smooth",
        "Sharpen":"Sharpen",
        "Contrast+":"Contrast+",
        "Contrast-":"Contrast-",
        "Grow":"Grow",
        "Shrink":"Shrink",
        "By Topo":"By Topo",
        "By Normals":"By Normals",
        "Mask Hide Tools:":"Mask Hide Tools:",
        
        
        ## Pie Left
        "Face Sets:":"Face Sets:",
        "All":"All",
        "Vis Invert":"Vis Invert",
        "Change Vis":"Change Vis",        
        "Create FaceSet：":"Create FaceSet：",
        "Visible":"Visible",
        "Loose":"Loose",
        "Random col":"Random col",
        "FaceBound":"FaceBound",
        "Seam":"Seam",
        "Normal":"Normal",
        "Bevel Weight":"Bevel Weight",
        "Crease":"Crease",
        "Sharp":"Sharp",
        "Fair Positions":"Fair Positions",
        "Fair Tangency":"Fair Tangency",
        "FaceSet to:":"FaceSet to:",        
        "VG":"VG",
        "Mat":"Mat",
        "Attr":"Attr",
        "UV":"UV",               
        "Select Copy to new objects":"Select Copy to new objects",        
        "Trim:":"Trim:",
        "Add Mesh:":"Add Mesh:",
        
        
        ### Pie Down
        "Mesh Filter:":"Mesh Filter:",
        "Surface Smooth":"Surface Smooth",
        "Inflate":"Inflate",
        "Relax":"Relax",
        "Relax FaceSet":"Relax FaceSet",
        "Enhance Details":"Enhance Details",
        "Erase Displacement":"Erase Displacement",
        "Mask Extract:":"Mask Extract:",
        "Extract":"Extract",
        "Slice":"Slice",
        "Fill Holes":"Fill Holes",
        "to New Obj":"to New Obj",
        
        ### pie UP
        "Hide":"Hide",
        "VisInvert":"VisInvert",
        
        
        #AddonPreferences          
        "Customize Pie Menu Shortcut:": "Customize Pie Menu Shortcut:",
        "Current Key:":"Current Key:",
        "Click set new shortcut":"Click set new shortcut",
        "How to set shortcut:":"How to set shortcut:",
        "1. Click 'Click set new shortcut' button":"1. Click 'Click set new shortcut' button",
        "2. Press any key combination (Ctrl+Shift+A, etc.)":"2. Press any key combination (Ctrl+Shift+A, etc.)",
        
        "Note: Changes will be saved automatically.": "Note: Changes will be saved automatically.",
        "Select Language:": "Select Language:",
        "Current language: ": "Current language: ",
        "Language": "Language",
        "Select interface language": "Select interface language",

    },
    
    
#################################################### 
# 中文   
####################################################    
    "zh_CN": {        
        ##### Pie界面 
        # Pie Right  
        "Boundary":"边界",
        "FaceSet Bonundary":"面组边界",
        "Edit Sel":"编辑选中",
        "Cavity":"槽边",
        "Color":"颜色",
        "Mask:": "遮罩蒙版:", 
        "Create Mask:":"创建遮罩:",        
        "Invert":"反选",
        "Clear":"清除",
        "Smooth":"光滑",
        "Sharpen":"锐化",
        "Contrast+":"对比度+",
        "Contrast-":"对比度-",
        "Grow":"扩选",
        "Shrink":"收缩",
        "By Topo":"拓布扩展",
        "By Normals":"法线扩展",
        "Mask Hide Tools:":"遮罩隐藏工具:",
        
        
        ## Pie Left
        "Face Sets:":"雕刻面组:",
        "All":"全显示",
        "Vis Invert":"可见反显",
        "Change Vis":"选中显示",        
        "Create FaceSet：":"创建雕刻面组：",
        "Visible":"可见-创建/清除",
        "Loose":"岛随机",
        "Random col":"随机颜色",
        "FaceBound":"面组边界",
        "Seam":"UV线",
        "Normal":"法线",
        "Bevel Weight":"倒角边权重",
        "Crease":"折痕边",
        "Sharp":"锐角边",
        "Fair Positions":"平顺位置",
        "Fair Tangency":"平顺切向",
        "FaceSet to:":"从雕刻面组到-->",        
        "VG":"点组",
        "Mat":"材质",
        "Attr":"属性",
        "UV":"UV",        
        "Select Copy to new objects":"选中-拷贝到新对象",                
        "Trim:":"修剪工具:",
        "Add Mesh:":"添加Mesh:",
        
        
        ### Pie  Down
        "Mesh Filter:":"网格滤镜:",
        "Surface Smooth":"表面光滑",
        "Inflate":"膨胀",
        "Relax":"松弛",
        "Relax FaceSet":"面组松弛",
        "Enhance Details":"表面细节增强",
        "Erase Displacement":"移除多级精度修改器雕刻效果",
        "Mask Extract:":"遮罩 挤出:",
        "Extract":"挤出",
        "Slice":"删除",
        "Fill Holes":"补洞",
        "to New Obj":"分离成新对象",
        
        ### Pie UP        
        "Hide":"隐藏",
        "VisInvert":"反显示",
        
        
        
        #AddonPreferences 
        "Customize Pie Menu Shortcut:": "自定义Pie菜单快捷键:",
        "Current Key:":"当前快捷键:",
        "Click set new shortcut":"单击设置新快捷键",
        
        "How to set shortcut:":"设置新快捷键的方法：",
        "1. Click 'Click set new shortcut' button":"1. 单击 '单击设置新快捷键' 按钮",
        "2. Press any key combination (Ctrl+Shift+A, etc.)":"2. 按下任意组合键（如:Ctrl+Shift+A等）",
          
        "Note: Changes will be saved automatically.": "注意：更改会自动保存。",
        "Select Language:": "选择语言:",
        "Current language: ": "当前语言: ",
        "Language": "语言",
        "Select interface language": "选择界面语言",
    }
}


def get_translation(lang_code, msg):
    """
    获取指定语言的翻译
    :param lang_code: 语言代码，如 'zh_CN', 'en_US'
    :param msg: 原始文本
    :return: 翻译后的文本，如果找不到则返回原始文本
    """
    return TRANSLATIONS.get(lang_code, {}).get(msg, msg)


def get_all_translations():
    """
    获取所有翻译字典
    用于注册到Blender的翻译系统
    """
    return TRANSLATIONS.copy()