import streamlit as st
import json
from zhipuai import ZhipuAI

# 页面配置
st.set_page_config(page_title="墩墩", page_icon="🤖")

# 初始化客户端
ZHIPU_API_KEY = st.secrets["ZHIPUAI_API_KEY"]
client = ZhipuAI(api_key=ZHIPU_API_KEY)
MODEL_NAME = "glm-4-flash"

# 标题
st.title("墩墩")
st.caption("基于智谱 GLM-4-Flash 模型驱动 | 中国电信知识库版")

# --- 读取 JSON 知识库 ---
@st.cache_data
def load_knowledge_base():
    try:
        # 【注意】请把下面的 '你的文件名.json' 改成你上传的真实文件名
        with open("你的文件名.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"读取知识库失败: {e}")
        return None

knowledge_data = load_knowledge_base()

# 显示知识库加载状态
if knowledge_data:
    st.success("✅ 知识库已加载")
else:
    st.warning("⚠️ 知识库未加载，请检查文件名")

# --- 对话逻辑 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("请输入关于电信的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 构建包含知识库的提示词
    system_prompt = "你是一个中国电信的知识助手。请根据以下参考资料回答用户问题。如果资料里没有相关信息，请礼貌告知用户。"
    
    # 将JSON数据转为字符串作为背景知识
    context = ""
    if knowledge_data:
        context = json.dumps(knowledge_data, ensure_ascii=False)
    
    full_prompt = f"{system_prompt}\n\n参考资料：\n{context}\n\n用户问题：{prompt}"

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"生成回答失败: {e}")
