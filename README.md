# 📦 LiteLocker

> 一个“阅后即焚”文件快递柜，让临时传输变得优雅且安全。


![Stars](https://img.shields.io/github/stars/xiaoguo141106/LiteLocker?style=flat-square)
![Forks](https://img.shields.io/github/forks/xiaoguo141106/LiteLocker?style=flat-square)
![Issues](https://img.shields.io/github/issues/xiaoguo141106/LiteLocker?color=yellow&style=flat-square)
![License](https://img.shields.io/badge/license-GPL--3.0-orange?style=flat-square)

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.20+-FF4B4B?style=flat-square&logo=streamlit)

---

### 🔗 快速链接
[ [项目首页](https://litelocker.streamlit.app/) |  [QQ群:](#) | [灵感来源: FileCodeBox](https://github.com/vastsa/FileCodeBox) ]

## 🚀 部署指南

### 方式一：使用 Docker 部署 (推荐)
这是最简单的方式，只需一行命令即可完成安装。

```bash
docker run -d \
  --name litelocker \
  -p 8501:8501 \
  -v /你的本地路径/data:/app/parcel_locker \
  --restart always \
  your-docker-username/litelocker:latest
```
## ✨ 功能特性
- **两页设计**：独立的“存入”与“提取”页面，逻辑清晰。
- **多类型支持**：支持各类文件上传及纯文本寄存。
- **自定义有效期**：内置“一小时”到“永久”选项，亦可自定义任意时长（小时/天/周/月）。
- **隐私保障**：文件存取过程完全保密，支持过期自动清理。

## 🛠️ 本地运行
1. 安装依赖：`pip install streamlit`
2. 启动程序：`python -m streamlit run app.py`

## 🛡️ 开源协议
本项目采用 [GPL-3.0](LICENSE) 协议。

## 鸣谢

本项目灵感源自开源项目 [FileCodeBox](https://github.com/vastsa/FileCodeBox)。
感谢原作者 [vastsa](https://github.com/vastsa) 提供的优秀产品思路。
本项目基于 Streamlit 进行了轻量化重新实现。
