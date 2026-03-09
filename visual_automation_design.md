# Visual Automation Agent 设计文档

## 🎯 目标
开发一个完全模拟用户行为的AI agent，使用视觉方案（截图+图像识别）而非DOM操作，解决Cloudflare认证问题。

## 🔧 技术栈
| 组件 | 技术选择 | 用途 |
|------|----------|------|
| 屏幕截图 | PyAutoGUI / Pillow | 捕获屏幕图像 |
| 图像识别 | OpenCV (模板匹配) | 定位按钮、输入框等元素 |
| 鼠标控制 | PyAutoGUI / pynput | 模拟点击、移动 |
| 键盘输入 | PyAutoGUI / pynput | 模拟打字、快捷键 |
| 浏览器连接 | Playwright | 连接已打开的Firefox实例 |
| 状态管理 | SQLite上下文数据库 | 记录操作历史、错误恢复 |
| 配置管理 | Python-dotenv | 管理环境变量 |

## 📁 项目结构
```
gpt-agent/visual_automation/
├── core/
│   ├── screen_capturer.py     # 屏幕截图模块
│   ├── image_locator.py       # 图像识别与定位
│   ├── input_simulator.py     # 鼠标键盘模拟
│   └── state_manager.py       # 状态机管理
├── tasks/
│   ├── browser_launcher.py    # 浏览器启动任务
│   ├── navigation_task.py     # 页面导航任务
│   ├── login_task.py          # 登录任务
│   └── chat_task.py           # 聊天任务
├── config/
│   ├── templates/             # 图像模板库
│   │   ├── chatgpt/
│   │   │   ├── login_button.png
│   │   │   ├── username_input.png
│   │   │   └── chat_input.png
│   │   └── common/
│   └── thresholds.yaml        # 识别阈值配置
├── tests/
│   ├── test_screenshot.py
│   ├── test_image_match.py
│   └── test_workflow.py
├── utils/
│   ├── logger.py
│   ├── error_handler.py
│   └── context_recorder.py    # 记录到本地上下文数据库
└── main.py                    # 主程序入口
```

## 🔄 工作流程

### 阶段1：环境准备
1. 用户手动打开Firefox浏览器
2. 登录目标网站（如ChatGPT），解决Cloudflare认证
3. 保持浏览器窗口打开并处于活动状态

### 阶段2：视觉自动化启动
```python
# 示例代码
from visual_automation.core.screen_capturer import ScreenCapturer
from visual_automation.core.image_locator import ImageLocator
from visual_automation.tasks.chat_task import ChatTask

# 初始化组件
capturer = ScreenCapturer()
locator = ImageLocator(template_dir="config/templates/chatgpt/")

# 执行聊天任务
task = ChatTask(capturer, locator)
task.send_message("Hello, this is a test message")
```

### 阶段3：图像识别流程
```
1. 截图当前屏幕
2. 加载目标元素模板（如"发送按钮"）
3. 使用OpenCV进行模板匹配
4. 计算匹配位置和置信度
5. 如果置信度 > 阈值，定位成功
6. 移动鼠标到该位置并点击
```

## 🎨 图像模板管理

### 模板采集
```bash
# 1. 手动截取目标元素
python scripts/capture_template.py --element login_button

# 2. 自动裁剪和优化
python scripts/process_template.py --input screenshot.png --output templates/login_button.png

# 3. 测试识别
python scripts/test_template.py --template templates/login_button.png
```

### 模板命名规范
```
{website}_{element}_{state}.png
示例: chatgpt_login_button_normal.png
       chatgpt_send_button_hover.png
```

## ⚙️ 配置系统

### config/thresholds.yaml
```yaml
matching:
  confidence_threshold: 0.85  # 匹配置信度阈值
  max_wait_seconds: 30        # 最大等待时间
  retry_attempts: 3           # 重试次数

screen:
  monitor: 0                  # 显示器编号
  region: [0, 0, 1920, 1080]  # 截图区域（可选）

input:
  click_delay: 0.1           # 点击间隔（秒）
  type_delay: 0.05           # 打字间隔（秒）
  human_variance: true       # 模拟人类操作差异
```

## 🔌 与现有系统集成

### 1. 替换现有DOM操作
```python
# 原代码（基于DOM）
await page.click("button[data-testid='login-button']")

# 新代码（基于视觉）
from visual_automation import click_element
click_element("login_button")  # 自动截图、识别、点击
```

### 2. 上下文记录
```python
from claw-context.local_context_manager import LocalContextManager

manager = LocalContextManager()
manager.record_test_result(
    test_name="视觉登录测试",
    browser="firefox",
    result="pass",
    screenshot_path="screenshots/login_success.png"
)
```

## 🧪 测试计划

### 单元测试
- [ ] 截图功能测试
- [ ] 图像匹配准确性测试
- [ ] 鼠标操作精度测试
- [ ] 键盘输入可靠性测试

### 集成测试
- [ ] ChatGPT完整登录流程
- [ ] 消息发送接收流程
- [ ] 长时间会话稳定性测试
- [ ] 多屏幕适配测试

### 性能测试
- [ ] 图像识别速度（<200ms）
- [ ] 完整操作延迟（<2s）
- [ ] 内存使用监控
- [ ] CPU占用优化

## 🚀 实施步骤

### 第1步：基础框架搭建（今天）
- 安装依赖包：`pip install pyautogui opencv-python pillow pynput`
- 创建项目目录结构
- 实现基本截图和图像匹配功能

### 第2步：核心模块开发（1-2天）
- 完成`screen_capturer.py`和`image_locator.py`
- 实现`input_simulator.py`（带人类化模拟）
- 创建基础任务类`BaseTask`

### 第3步：ChatGPT任务实现（2-3天）
- 采集ChatGPT界面元素模板
- 实现`login_task.py`和`chat_task.py`
- 集成到现有`gpt_agent.py`

### 第4步：测试与优化（2天）
- 完整流程测试
- 错误处理和恢复机制
- 性能优化和配置调优

## ⚠️ 挑战与解决方案

### 挑战1：屏幕分辨率差异
**解决方案**：使用相对坐标或模板匹配，支持多种分辨率

### 挑战2：页面动态变化
**解决方案**：多模板匹配 + 动态更新模板库

### 挑战3：网络延迟和加载
**解决方案**：智能等待机制 + 超时重试

### 挑战4：安全性
**解决方案**：本地存储敏感数据，不记录密码，仅模拟已登录会话

## 📈 成功指标
1. 登录成功率 > 95%
2. 消息发送成功率 > 98%
3. 单次操作延迟 < 2秒
4. 连续运行稳定性 > 24小时

---
**创建时间**: 2026-03-08 19:35 GMT+8  
**版本**: 1.0.0  
**更新记录**: 存入本地上下文数据库