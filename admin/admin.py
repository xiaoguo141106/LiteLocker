import streamlit as st
import os
import time
from datetime import datetime

# 页面配置
st.set_page_config(page_title="LiteLocker 后台管理", page_icon="🔐")

# --- 登录逻辑 ---
ADMIN_PASSWORD = "asdasd123321xg"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 管理员登录")
    pwd = st.text_input("请输入管理密码", type="password")
    if st.button("登录"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("密码错误")
    st.stop()

# --- 管理界面 ---
st.title("🛠️ 快递柜后台管理")
SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "parcel_locker")

if st.button("退出登录"):
    st.session_state.logged_in = False
    st.rerun()

if not os.path.exists(SAVE_DIR):
    st.info("暂无数据目录")
else:
    files = [f for f in os.listdir(SAVE_DIR) if "_" in f]
    if not files:
        st.info("柜子里目前是空的")
    else:
        for f_name in files:
            parts = f_name.split("_", 3)
            if len(parts) < 4: continue
            
            code, ts, p_type, real_name = parts[0], parts[1], parts[2], parts[3]
            expire_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d %H:%M')
            
            with st.expander(f"📦 {code} - {real_name}"):
                st.write(f"**过期时间:** {expire_str} | **类型:** {'文件' if p_type=='F' else '便签'}")
                
                # 修改取件码
                new_code = st.text_input("修改取件码", value=code, key=f"edit_{f_name}").upper()
                
                col1, col2 = st.columns(2)
                if col1.button("保存修改", key=f"save_{f_name}"):
                    new_f_name = f"{new_code}_{ts}_{p_type}_{real_name}"
                    os.rename(os.path.join(SAVE_DIR, f_name), os.path.join(SAVE_DIR, new_f_name))
                    st.success("修改成功！")
                    st.rerun()
                
                if col2.button("🗑️ 立即删除", key=f"del_{f_name}"):
                    os.remove(os.path.join(SAVE_DIR, f_name))
                    st.warning("已删除")
                    st.rerun()