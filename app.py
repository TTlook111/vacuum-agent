import streamlit as st
from agent.react_agent import ReactAgent
from rag.vector_store import VectorStoreService

# 配置页面
st.set_page_config(
    page_title="Vacuum Agent - 扫地机器人智能助手",
    page_icon="🤖",
    layout="wide"
)

# 侧边栏：知识库管理与系统状态
with st.sidebar:
    st.header("⚙️ 系统管理")
    st.markdown("---")
    st.subheader("📚 知识库状态")
    
    if st.button("🔄 更新/构建知识库", use_container_width=True):
        with st.spinner("正在解析文档并构建向量库，请稍候..."):
            try:
                vs_service = VectorStoreService()
                vs_service.load_document()
                st.success("知识库更新成功！")
            except Exception as e:
                st.error(f"知识库构建失败: {str(e)}")
                
    st.markdown("*(点击上方按钮将 `data/` 目录下的最新文件入库)*")
    
    st.markdown("---")
    st.markdown("### 🛠️ 可用工具")
    st.markdown("- 📖 知识库检索 (RAG)\n- 🌤️ 城市天气查询\n- 📍 用户位置查询\n- 👤 用户ID查询\n- 📊 外部历史数据对比")

# 页面标题和描述
st.title("🤖 Vacuum Agent 智能助手")
st.markdown("你好！我是专注于**扫地机器人**领域的智能助手。无论是选购指南、维护保养，还是故障排除，都可以问我哦！")

# 初始化 Agent 实例 (存入 session_state 以避免重复初始化)
if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题，例如：扫地机器人日常如何保养？"):
    # 将用户输入添加到历史并展示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 生成并展示助手的回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 调用 Agent 的流式输出方法
            for chunk in st.session_state.agent.execute_stream(prompt):
                full_response = chunk
                # 添加闪烁光标效果，增强交互体验
                message_placeholder.markdown(full_response + "▌")
            
            # 最终结果去掉光标
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            full_response = "抱歉，我遇到了一些问题，请稍后再试。"
            
    # 将助手回复添加到历史
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
