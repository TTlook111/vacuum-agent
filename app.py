import streamlit as st
from agent.react_agent import ReactAgent
from rag.vector_store import VectorStoreService

# 配置页面
st.set_page_config(
    page_title="Vacuum Agent | 智能扫地机器人中枢",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入自定义 CSS 美化界面 (科技感与清洁感结合的美学方向)
st.markdown("""
<style>
    /* 全局字体设定 */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    .stApp {
        font-family: 'Outfit', sans-serif;
    }
    
    /* 标题发光效果 */
    h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem !important;
    }
    
    /* 聊天气泡样式美化 (仅添加圆角和阴影，不覆盖颜色以免破坏 Streamlit 的深色模式) */
    [data-testid="stChatMessage"] {
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 用户气泡特别样式 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-bottom-right-radius: 0;
    }
    
    /* AI气泡特别样式 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-bottom-left-radius: 0;
        background: rgba(56, 189, 248, 0.03) !important;
        border: 1px solid rgba(56, 189, 248, 0.1);
    }
    
    /* 侧边栏玻璃拟态增强 */
    [data-testid="stSidebar"] {
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 按钮美化 */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(56, 189, 248, 0.2);
        border-color: #38bdf8 !important;
    }
    
    /* Markdown 链接颜色 */
    a {
        color: #38bdf8 !important;
        text-decoration: none;
        transition: color 0.2s;
    }
    a:hover {
        color: #7dd3fc !important;
    }
    
    /* 装饰元素：科技感发光球 */
    .glow-orb {
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(56,189,248,0.1) 0%, rgba(0,0,0,0) 70%);
        top: -200px;
        right: -200px;
        z-index: -1;
        pointer-events: none;
    }
    
    /* Created By Deerflow 品牌标志 - 悬浮角落标签 */
    .deerflow-badge {
        position: fixed;
        bottom: 24px;
        right: 24px;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 100px;
        color: rgba(255, 255, 255, 0.5) !important;
        font-family: 'Outfit', sans-serif;
        font-size: 12px;
        font-weight: 500;
        text-decoration: none;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        z-index: 9999;
        overflow: hidden;
    }
    
    .deerflow-badge::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(129, 140, 248, 0.1));
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .deerflow-badge .star {
        color: #38bdf8;
        font-size: 14px;
        transition: transform 0.4s ease;
    }
    
    .deerflow-badge:hover {
        color: #f8fafc !important;
        border-color: rgba(56, 189, 248, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(56, 189, 248, 0.2);
    }
    
    .deerflow-badge:hover::before {
        opacity: 1;
    }
    
    .deerflow-badge:hover .star {
        transform: rotate(180deg) scale(1.2);
    }
</style>

<!-- 注入背景装饰和品牌标志 -->
<div class="glow-orb"></div>
<a href="https://deerflow.tech" target="_blank" class="deerflow-badge">
    <span class="star">✦</span>
    <span>Created By Deerflow</span>
</a>
""", unsafe_allow_html=True)

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
    st.markdown("- 📖 知识库检索 (RAG)\n- 🌤️ 城市天气查询\n- 🌬️ 空气质量分析\n- 📍 用户位置查询\n- 👤 用户ID查询\n- 📊 外部历史数据对比")

# 页面标题和描述
st.title("✨ Vacuum Agent 中枢")
st.markdown("你好！我是专注于**扫地机器人**领域的智能助手。无论是选购指南、维护保养，还是结合实时天气与空气质量的清洁建议，我都能为您解答！")

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
