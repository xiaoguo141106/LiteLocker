import streamlit as st
import os
import time
import hashlib

def show_admin():
    st.title("🛠️ 柜内包裹监控中心")
    
    # --- 1. 登录校验逻辑 ---
    if "admin_auth" not in st.session_state:
        st.session_state.admin_auth = False

    if not st.session_state.admin_auth:
        st.info("💡 提示：管理员密码哈希值需配置在 .streamlit/secrets.toml 中")
        pwd_input = st.text_input("请输入管理员密码", type="password")
        
        if st.button("登录"):
            # 将用户输入的密码进行 SHA-256 哈希处理
            input_hash = hashlib.sha256(pwd_input.encode()).hexdigest()
            
            # 从 st.secrets 读取预设的哈希值进行比对
            try:
                target_hash = st.secrets["ADMIN_HASH"]
                if input_hash == target_hash:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("密码错误，请检查！")
            except Exception:
                st.error("未检测到 ADMIN_HASH 配置，请检查 secrets.toml")
        return # 未登录则拦截，不执行后续代码

    # --- 2. 顶部管理栏 ---
    col_header, col_logout = st.columns([5, 1])
    with col_header:
        st.success("欢迎回来，管理员！")
    with col_logout:
        if st.button("退出登录"):
            st.session_state.admin_auth = False
            st.rerun()

    # --- 3. 包裹列表管理 ---
    SAVE_DIR = "parcel_locker"
    
    # 确保目录存在
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    file_list = os.listdir(SAVE_DIR)
    
    if not file_list:
        st.info("目前快递柜是空的，暂无包裹。")
        return

    st.write(f"📊 当前共有 **{len(file_list)}** 个包裹")

    for f_name in file_list:
        # 跳过隐藏文件或非协议格式文件
        if not f_name.count("_") >= 5:
            continue
            
        try:
            # 解析协议：取件码_过期戳_最大次_已下次_类型_原名
            parts = f_name.split("_", 5)
            old_code = parts[0]
            real_name = parts[5]
            
            with st.expander(f"📦 【{old_code}】 {real_name}"):
                # 布局：左侧修改信息，右侧危险操作
                col_edit, col_del = st.columns([3, 1])
                
                with col_edit:
                    new_code = st.text_input(
                        "修改取件码", 
                        value=old_code, 
                        key=f"in_{f_name}",
                        max_chars=12
                    ).upper().strip().replace("_", "") # 强制大写，去空格，去下划线
                    
                    if st.button("💾 保存修改", key=f"btn_{f_name}"):
                        if new_code != old_code and new_code != "":
                            # 重新组合文件名并重命名
                            new_f_name = f"{new_code}_{parts[1]}_{parts[2]}_{parts[3]}_{parts[4]}_{parts[5]}"
                            try:
                                os.rename(
                                    os.path.join(SAVE_DIR, f_name), 
                                    os.path.join(SAVE_DIR, new_f_name)
                                )
                                st.success(f"修改成功：{old_code} -> {new_code}")
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"修改失败: {e}")
                
                with col_del:
                    st.write("") # 间距
                    st.write("") 
                    if st.button("🔥 彻底销毁", key=f"del_{f_name}", help="此操作不可恢复"):
                        try:
                            os.remove(os.path.join(SAVE_DIR, f_name))
                            st.rerun()
                        except Exception as e:
                            st.error("删除失败")
                                
        except Exception:
            continue
