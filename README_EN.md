# 📦 LiteLocker

> A "self-destructing" file locker that makes temporary transfers elegant and secure.

---

### 🔗 Quick Links

[ [Demo](https://litelocker.streamlit.app/) | [QQ Group:](#) | [Inspiration: FileCodeBox](https://github.com/vastsa/FileCodeBox) ]

## 🚀 Deployment Guide

### Method 1: Deploy with Docker (Recommended)

The simplest way—complete installation with a single command.

```bash
docker run -d \
  --name litelocker \
  -p 8501:8501 \
  -v /your/local/path/data:/app/parcel_locker \
  --restart always \
  your-docker-username/litelocker:latest

```

## ✨ Key Features

* **Two-Page Design**: Independent "Deposit" and "Retrieve" pages for clear logic.
* **Multi-Type Support**: Supports various file uploads and plain text storage.
* **Custom Expiration**: Built-in options from "1 hour" to "Permanent," with support for custom durations (hours/days/weeks/months).
* **Privacy Protection**: The file storage and retrieval process is fully confidential, with support for automatic cleanup upon expiration.

## 🛠️ Local Execution

1. Install dependencies: `pip install streamlit`
2. Start the program: `python -m streamlit run app.py`

## 🛡️ License

This project is licensed under [GPL-3.0](https://www.google.com/search?q=LICENSE).

## Credits

This project is a lightweight re-implementation inspired by [FileCodeBox](https://github.com/vastsa/FileCodeBox).
- **Original Author**: [vastsa](https://github.com/vastsa)
- **License**: This project is licensed under the GPL-3.0 License (derived from LGPL-3.0).
