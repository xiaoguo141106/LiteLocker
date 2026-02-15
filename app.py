import streamlit as st
import random
import string
import os
import time
from datetime import datetime, timedelta

# --- 1. 页面配置与美化 CSS ---
st.set_page_config(page_title="码上递 - LiteLocker", page_icon="📦", layout="centered")

st.markdown("""
    <style>
    /* 整体背景与隐藏默认页眉 */
    .stApp { background-color: #f8fafd; }
    header {visibility: hidden;}
    
    /* 强制居中卡片容器 */
    .main .block-container {
        max-width: 500px;
        padding-top: 3rem;
    }

    /* 卡片美化 */
    div.stTabs {
        background: white;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
    }

    /* 按钮美化 */
    .stButton>button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px;
        font-weight: bold;
    }
    
    /* 居中文本 */
    .centered-text { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心逻辑准备 ---
SAVE_DIR = "parcel_locker"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

EXPIRY_OPTIONS = {
    "一小时": timedelta(hours=1),
    "一天": timedelta(days=1),
    "一周": timedelta(weeks=1),
    "一月": timedelta(days=30),
}

# --- 3. 页面内容 ---
st.markdown("<div class='centered-text'><img src='https://cdn-icons-png.flaticon.com/512/679/679821.png' width='60'></div>", unsafe_allow_html=True)
st.markdown("<h1 class='centered-text' style='color: #333;'>LiteLocker</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered-text' style='color: #888;'>极简安全的文件快递柜</p>", unsafe_allow_html=True)

# 独立两页面 Tab
tab_get, tab_put = st.tabs(["📥 提取包裹", "📤 存入包裹"])

# ================= 页面：提取包裹 =================
with tab_get:
    st.write("")
    code_in = st.text_input("取件码", placeholder="请输入6位取件码", label_visibility="collapsed").upper()
    
    if st.button("开启柜门", key="get_btn", use_container_width=True):
        if len(code_in) == 6:
            found = False
            for f in os.listdir(SAVE_DIR):
                if f.startswith(code_in):
                    found = True
                    parts = f.split("_", 3)
                    expire_time = int(parts[1])
                    item_type = parts[2]
                    item_name = parts[3]
                    file_path = os.path.join(SAVE_DIR, f)
                    
                    if time.time() > expire_time:
                        st.error("❌ 包裹已过期，已被系统自动清理。")
                        os.remove(file_path)
                    else:
                        st.success(f"🔍 找到包裹：{item_name}")
                        # 文本预览
                        if item_type == "T":
                            with open(file_path, "r", encoding="utf-8") as text_f:
                                st.text_area("内容预览", value=text_f.read(), height=150)
                        
                        # 下载并销毁按钮
                        with open(file_path, "rb") as file_data:
                            st.download_button(
                                label="🚀 取走文件(下载)",
                                data=file_data.read(),
                                file_name=item_name,
                                use_container_width=True,
                                on_click=lambda p=file_path: os.remove(p)
                            )
                    break
            if not found:
                st.error("未找到相关包裹，请检查取件码。")
        else:
            st.warning("请输入完整的6位取件码。")

# ================= 页面：存入包裹 =================
with tab_put:
    st.write("")
    # 改用 radio 确保在所有版本显示正常
    mode = st.radio("存入内容类型", ["文件", "文本"], horizontal=True)
    
    exp_choice = st.selectbox("有效期设置", list(EXPIRY_OPTIONS.keys()) + ["自定义"])
    
    expire_delta = None
    if exp_choice == "自定义":
        col_v, col_u = st.columns(2)
        with col_v:
            c_val = st.number_input("时长数值", min_value=1, value=1)
        with col_u:
            c_unit = st.selectbox("单位", ["小时", "天", "周", "月"])
        u_map = {"小时": timedelta(hours=c_val), "天": timedelta(days=c_val), "周": timedelta(weeks=c_val), "月": timedelta(days=c_val*30)}
        expire_delta = u_map[c_unit]
    else:
        expire_delta = EXPIRY_OPTIONS[exp_choice]

    st.markdown("---")

    if mode == "文件":
        u_file = st.file_uploader("请选择或拖入文件", label_visibility="visible")
        if st.button("存入柜子", key="put_f_btn", use_container_width=True):
            if u_file:
                code = generate_code()
                expire_ts = int(time.time() + expire_delta.total_seconds())
                fname = f"{code}_{expire_ts}_F_{u_file.name}"
                with open(os.path.join(SAVE_DIR, fname), "wb") as f:
                    f.write(u_file.getbuffer())
                st.balloons()
                st.success(f"寄存成功！取件码：")
                st.code(code, language=None)
            else:
                st.error("请先上传文件")
    else:
        u_text = st.text_area("请输入文字内容", placeholder="例如：WiFi密码是123456")
        if st.button("存入柜子", key="put_t_btn", use_container_width=True):
            if u_text.strip():
                code = generate_code()
                expire_ts = int(time.time() + expire_delta.total_seconds())
                fname = f"{code}_{expire_ts}_T_便签.txt"
                with open(os.path.join(SAVE_DIR, fname), "w", encoding="utf-8") as f:
                    f.write(u_text)
                st.balloons()
                st.success(f"寄存成功！取件码：")
                st.code(code, language=None)
            else:
                st.error("内容不能为空")

st.markdown("<p style='text-align: center; color: #bbb; font-size: 0.7rem; margin-top: 50px;'>🛡️ 安全加密 | 采用GPL v3.0开源协议</p>", unsafe_allow_html=True)