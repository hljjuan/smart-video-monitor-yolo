# 🛡️ 智能视频监控与决策分析平台 (Smart Video Monitoring Platform)

基于 **YOLO 深度学习目标检测** 与 **OpenCV 计算机视觉** 的现代化安防监控平台。用户只需上传监控视频，系统即可自动逐帧解析、识别人员，并精准判断“禁入区”入侵事件，最终生成可视化数据大屏与 AI 智能决策报告。

## ✨ 核心功能

- 🎯 **AI 目标检测**：基于 YOLO 模型，实时检测画面中的 `Person`。
- 🚧 **区域入侵研判**：基于 OpenCV `pointPolygonTest` 算法，实时判断人员是否进入自定义多边形禁入区。
- ⏱️ **告警冷却去重**：内置“帧级冷却”机制，防止同一目标滞留导致的海量重复告警。
- 📊 **数据可视化大屏**：基于 Vue3 + ECharts，实时展示任务总数、告警频次及客流趋势。
- 🤖 **智能决策报告**：内置数据分析引擎，自动生成安全态势评估与行动建议。
- ⚡ **异步处理架构**：后端使用 FastAPI BackgroundTasks 实现异步处理，前端轮询进度，避免页面卡顿。

## 🛠️ 技术栈

**前端 (Frontend):**
- Vue 3 + Vite
- Element Plus (UI 组件库)
- ECharts (数据可视化)
- Axios (HTTP 请求)

**后端 (Backend):**
- Python 3.10+
- FastAPI (Web 框架)
- Ultralytics (YOLO 推理)
- OpenCV (图像处理)
- SQLite (数据持久化)

## 📸 系统截图

*(建议上传几张你系统的截图替换掉下面的占位符)*
- **数据总览与可视化大屏**
- **视频检测与区域入侵告警**
- **智能决策分析报告**

## 🚀 快速开始

### 1. 启动后端 (FastAPI)
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动后端服务 (默认 8000 端口)
uvicorn app.main:app --reload
启动前端 (Vue3)
# 进入前端目录
cd frontend

# 安装前端依赖
npm install

# 启动前端服务 (默认 5173 端口)
📁 项目结构
npm run dev
├── app/                 # 后端核心代码
│   ├── core/            # YOLO 与 OpenCV 算法封装
│   ├── main.py          # FastAPI 接口与路由
│   └── database.py      # 数据库操作模块
├── frontend/            # Vue3 前端工程
│   ├── src/views/       # 页面组件 (大屏/检测/告警)
│   └── vite.config.js   # 前端代理配置
├── data/                # 测试数据目录
└── requirements.txt     # Python 依赖清单
许可证
本项目仅供学习与交流使用，采用 MIT License

---

### 💡 贴完之后的优化小建议：
1. **加标签（Topics）**：去你的仓库主页右侧，点击 `About` 旁边的齿轮 ⚙️，在 `Topics` 里加上：`yolo`、`opencv`、`fastapi`、`vue3`、`computer-vision`、`object-detection`。
2. **清理多余文件**：你的主页上有一个 `main.py` 和一个 `project` 文件夹。如果是之前学习测试的代码，可以留着，但最好确认一下 `main.py` 有没有用，没用的话可以在网页上直接删掉。
3. **上传截图**：在网页上点击 `Add file` -> `Upload files`，把你系统跑起来的截图传上去，然后把 README 里的占位符换成图片的链接。
