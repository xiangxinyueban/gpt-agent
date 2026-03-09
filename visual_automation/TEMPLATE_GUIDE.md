# 模板采集指南

## 为什么需要模板？

Visual Automation Agent使用图像模板匹配来识别屏幕上的UI元素。没有模板，系统无法工作。

## 模板目录结构

```
visual_automation/config/templates/
├── chatgpt/          # ChatGPT特定模板
├── cloudflare/       # Cloudflare验证模板  
└── common/           # 通用模板（按钮、输入框等）
```

## 快速开始：创建基础模板

### 方法1：手动截图（推荐）

1. **准备目标页面**
   - 打开Firefox浏览器
   - 导航到ChatGPT登录页面
   - 确保页面完全加载

2. **采集登录按钮模板**
   ```bash
   # 运行截图工具
   python scripts/capture_template.py --element chatgpt_login_button
   ```
   
3. **按照提示操作**
   - 将鼠标悬停在登录按钮上
   - 按下指定快捷键截图
   - 调整裁剪区域
   - 保存为`chatgpt_login_button.png`

### 方法2：使用现有截图（快速）

如果你已经有截图，可以手动裁剪：

1. 打开截图文件
2. 使用图像编辑工具裁剪目标元素
3. 保存到对应的模板目录
4. 命名规范：`{website}_{element}_{state}.png`
   - 示例：`chatgpt_login_button_normal.png`

## 必需的基础模板

### ChatGPT模板
- `chatgpt_login_button.png` - 登录按钮
- `chatgpt_username_field.png` - 用户名输入框
- `chatgpt_password_field.png` - 密码输入框  
- `chatgpt_human_checkbox.png` - 人机验证复选框
- `chatgpt_submit_button.png` - 提交按钮

### Cloudflare模板
- `cloudflare_turnstile_checkbox.png` - Turnstile复选框
- `cloudflare_verify_button.png` - 验证按钮
- `cloudflare_success_indicator.png` - 验证成功指示器

### 通用模板
- `common_button.png` - 通用按钮
- `common_input_field.png` - 通用输入框
- `common_checkbox.png` - 通用复选框

## 模板质量要求

1. **清晰度**：元素边缘清晰，无模糊
2. **大小**：适当大小，不要太小（至少32x32像素）
3. **背景**：尽量少包含背景，专注于元素本身
4. **状态**：捕获元素的正常状态（非悬停、非点击）

## 测试模板

```bash
# 测试单个模板
python scripts/test_template.py --template chatgpt_login_button.png

# 测试所有模板
python scripts/test_all_templates.py
```

## 自动模板生成（开发中）

我们正在开发自动模板采集系统：

```python
from visual_automation.template_manager import TemplateManager

manager = TemplateManager()
# 交互式采集
manager.capture_template("chatgpt_login_button")
# 批量采集
manager.capture_multiple(["username_field", "password_field", "login_button"])
```

## 故障排除

### 问题：模板匹配失败
**可能原因**：
- 屏幕分辨率不同
- 页面样式变化
- 元素状态变化（悬停、禁用等）

**解决方案**：
1. 采集多个状态的模板
2. 使用相对匹配（降低置信度阈值）
3. 定期更新模板

### 问题：找不到元素
**检查**：
1. 模板文件是否存在且命名正确
2. 模板目录路径是否正确配置
3. 屏幕截图是否成功

## 下一步

1. 创建基础模板库
2. 测试模板匹配准确性
3. 优化匹配参数
4. 建立模板更新机制