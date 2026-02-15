import streamlit as st
import hashlib

# 假设你的原始密码是 asdasd123321xg
raw_password = "asdasd123321xg"

# 使用 SHA-256 算法加密
password_hash = hashlib.sha256(raw_password.encode()).hexdigest()
print(f"你的加密指纹是: {password_hash}")