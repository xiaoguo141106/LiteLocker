import streamlit as st
import os
import time
import random
import string
from datetime import datetime

# --- 核心路由逻辑 ---
# 获取网址参数，例如：your-url.com/?page=admin
query_params = st.query_params
#
if query_params.get("page") == "admin":
    # 如果网址带了 admin 参数，则运行 admin 文件夹下的代码
    try:
        # 这里直接导入并执行 admin 文件夹下的逻辑
        from admin.admin import show_admin
        show_admin()
    except ImportError:
        st.error("找不到 admin/admin.py 文件或 show_admin 函数")
    
    # 提供一个返回主页的按钮
    if st.sidebar.button("返回首页"):
        st.query_params.clear()
        st.rerun()
    st.stop() # 停止运行后面的主页代码

# --- 页面配置 ---
st.set_page_config(page_title="LiteLocker - 极简快递柜", page_icon="📦", layout="wide")

# --- 常量定义 ---
SAVE_DIR = "parcel_locker"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- 样式美化 (官网 Hero 风格) ---
st.markdown("""
    <style>
    .hero {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    .stButton>button { width: 100%; border-radius: 8px; }
    </style>
    <div class="hero">
        <h1>📦 LiteLocker (码上递)</h1>
        <p>支持限时、限次领取的极简安全传输工具</p>
    </div>
""", unsafe_allow_html=True)

# --- 核心函数 ---
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- 主界面布局 ---
tab1, tab2 = st.tabs(["🚀 提取包裹", "📤 存入包裹"])

# --- Tab 1: 提取逻辑 ---
# --- Tab 1: 提取逻辑 ---
with tab1:
    st.markdown("### 🚀 提取包裹")
    get_code = st.text_input("请输入 6 位取件码", placeholder="例如: A1B2C3", label_visibility="collapsed").upper()
    
    if st.button("开启柜门", key="get_btn"):
        if get_code:
            found = False
            # 遍历保存目录寻找匹配的文件
            for f_name in os.listdir(SAVE_DIR):
                if f_name.startswith(get_code):
                    found = True
                    file_path = os.path.join(SAVE_DIR, f_name)
                    
                    # 1. 解析文件名 (协议：取件码_过期戳_最大次_已下次_类型_原名)
                    parts = f_name.split("_", 5)
                    expire_ts = int(parts[1])
                    max_d = int(parts[2])
                    curr_d = int(parts[3])
                    p_type = parts[4]  # F 为文件, T 为文本
                    real_name = parts[5]
                    
                    # 2. 检查是否过期或达到次数上限
                    now = int(time.time())
                    if now > expire_ts:
                        os.remove(file_path)
                        st.error("⏰ 该包裹已超过有效期，已自动销毁。")
                        break
                    if max_d != 0 and curr_d >= max_d:
                        os.remove(file_path)
                        st.error("🚫 该包裹下载次数已达上限，已自动销毁。")
                        break
                    
                    # 3. 提取成功 - 根据类型展示内容
                    st.success(f"✅ 成功找到包裹：{real_name}")
                    
                    if p_type == "T":
                        # 如果是文本模式，直接读出来展示在网页上
                        with open(file_path, "r", encoding="utf-8") as f:
                            text_content = f.read()
                        st.text_area("📝 文本内容：", value=text_content, height=200)
                        st.caption("您可以直接复制上方文字内容。")
                    
                    # 4. 提供下载按钮 (无论是文件还是文本都支持下载)
                    with open(file_path, "rb") as f:
                        if st.download_button("💾 点击下载包裹", f, file_name=real_name):
                            # 更新下载次数逻辑
                            new_curr = curr_d + 1
                            new_f_name = f"{parts[0]}_{parts[1]}_{parts[2]}_{new_curr}_{parts[4]}_{parts[5]}"
                            os.rename(file_path, os.path.join(SAVE_DIR, new_f_name))
                            
                            # 判定是否需要立即销毁（如果是最后一次提取）
                            if max_d != 0 and new_curr >= max_d:
                                st.warning("这是最后一次有效提取，包裹已从服务器销毁。")
                            st.rerun() # 刷新状态
                    break
            
            if not found:
                st.error("❌ 未找到匹配的包裹，请检查取件码是否正确。")
        else:
            st.warning("⚠️ 请先输入取件码。")

# --- Tab 2: 存入逻辑 ---
# with tab2:
#     st.subheader("存入新包裹")
#     uploaded_file = st.file_uploader("选择文件", type=None)
    
#     with st.expander("🛡️ 销毁规则设置"):
#         col_h, col_c = st.columns(2)
#         with col_h:
#             hours = st.number_input("有效期 (小时)", min_value=1, max_value=720, value=24)
#         with col_c:
#             max_d = st.number_input("提取次数上限 (0为无限)", min_value=0, max_value=100, value=1)
            
#     if st.button("生成取件码", key="save_btn"):
#         if uploaded_file:
#             code = generate_code()
#             expire_ts = int(time.time() + hours * 3600)
#             # 命名协议
#             save_name = f"{code}_{expire_ts}_{max_d}_0_F_{uploaded_file.name}"
#             with open(os.path.join(SAVE_DIR, save_name), "wb") as f:
#                 f.write(uploaded_file.getbuffer())
            
#             st.balloons()
#             st.success("存入成功！")
#             st.code(f"您的取件码为: {code}", language="markdown")
#             st.info(f"将在 {hours} 小时后或提取 {max_d if max_d!=0 else '无限'} 次后自动销毁。")
#         else:
#             st.error("请先上传文件")
# --- 在 Tab 2: 存入逻辑 中替换以下部分 ---
with tab2:
    st.markdown("### 📥 存入新包裹")
    
    # 1. 让用户选择存入模式
    save_mode = st.radio("选择存入模式", ["上传文件", "输入文本内容"], horizontal=True, label_visibility="collapsed")
    
    content_to_save = None
    p_type = "F"  # 默认为文件 (File)
    original_name = ""

    if save_mode == "上传文件":
        uploaded_file = st.file_uploader("选择文件", type=None, label_visibility="collapsed")
        if uploaded_file:
            content_to_save = uploaded_file.getbuffer()
            original_name = uploaded_file.name
            p_type = "F"
    else:
        text_content = st.text_area("在此输入文本内容", placeholder="把你想传的内容粘在这里...", height=150)
        if text_content:
            content_to_save = text_content.encode('utf-8')
            # 文本模式下，我们起一个虚拟文件名，方便后面解析
            original_name = "text_note.txt"
            p_type = "T" # 标记为文本 (Text)

    # 2. 销毁规则设置（你要求的对齐版）
    col_val, col_unit = st.columns([3, 1])
    with col_unit:
        unit = st.selectbox("\u00A0", ["天", "小时", "分钟", "次"], label_visibility="visible")
    with col_val:
        label_text = f"有效{'次数' if unit == '次' else '时长'} (0为永久)"
        val = st.number_input(label_text, min_value=0, value=1, step=1)

    # 3. 保存逻辑
    if st.button("🚀 安全寄送"):
        if content_to_save:
            code = generate_code()
            
            # 销毁逻辑计算
            if val == 0:
                expire_ts = int(time.time() + 10 * 365 * 24 * 3600)
                max_d = 0
            else:
                if unit == "次":
                    max_d = val
                    expire_ts = int(time.time() + 30 * 86400)
                else:
                    max_d = 0
                    mult = {"天": 86400, "小时": 3600, "分钟": 60}
                    expire_ts = int(time.time() + val * mult[unit])

            # 命名协议：取件码_过期戳_最大次_已下次_类型_原名
            save_name = f"{code}_{expire_ts}_{max_d}_0_{p_type}_{original_name}"
            with open(os.path.join(SAVE_DIR, save_name), "wb") as f:
                f.write(content_to_save)
            
            st.success(f"寄送成功！取件码：{code}")
            status = "永久有效" if val == 0 else f"将在 {val} {unit} 后销毁"
            st.info(f"💡 状态：{status}")
        else:
            st.error("请先上传文件或输入文本内容")
# --- 页脚数据统计 ---
st.divider()
st.caption("LiteLocker v1.0.0 | 安全 · 私密 · 高效")
