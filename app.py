import streamlit as st
from openai import OpenAI

# ==========================================
# ⚙️ 配置区域 (已自动填入你的密钥)
# ==========================================

# 1. 智谱 AI API Key (已填入)
 

# 2. 智谱 AI 的接口地址
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
import streamlit as st
ZHIPU_API_KEY = st.secrets["ZHIPUAI_API_KEY"]
# 3. 使用的免费模型名称 (GLM-4-Flash 目前免费且速度快)
MODEL_NAME = "glm-4-flash"

# ==========================================
# 🎨 界面设置
# ==========================================
st.set_page_config(page_title="墩墩", page_icon="🤖")
st.title("🤖 墩墩")
st.caption("基于智谱 GLM-4-Flash 模型驱动 | 永久免费额度")

# ==========================================
# 💬 聊天逻辑
# ==========================================

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史聊天记录
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入你的问题..."):
    # 1. 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. 将用户消息加入历史
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. 调用 AI 模型
    try:
        client = OpenAI(
            api_key=ZHIPU_API_KEY,
            base_url=ZHIPU_BASE_URL
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # 发送请求给智谱 AI
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True
            )
            
            # 逐字显示回复（打字机效果）
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # 4. 将 AI 回复加入历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    except Exception as e:
        st.error(f"出错了：{str(e)}")
        st.info("提示：请检查密钥是否正确，或网络是否通畅。")