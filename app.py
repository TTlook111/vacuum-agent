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
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(10px);
    }
    
    /* 用户气泡特别样式 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-bottom-right-radius: 0;
        border-left: 4px solid #818cf8;
    }
    
    /* AI气泡特别样式 */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-bottom-left-radius: 0;
        background: rgba(56, 189, 248, 0.05) !important;
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-left: 4px solid #38bdf8;
    }
    
    /* 思考过程 Expander 样式美化 */
    [data-testid="stExpander"] {
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 0.75rem !important;
        background: rgba(15, 23, 42, 0.5) !important;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    [data-testid="stExpander"] summary {
        color: #7dd3fc !important;
        font-family: 'Outfit', sans-serif;
        font-size: 0.9rem !important;
    }
    
    [data-testid="stExpander"] p, [data-testid="stExpander"] li {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        line-height: 1.5 !important;
    }
    
    /* Expander 内部的代码块样式 */
    [data-testid="stExpander"] pre {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    [data-testid="stExpander"] code {
        color: #a78bfa !important;
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
    st.markdown("- 🎮 **设备控制** (启动/暂停/回充)\n- 🩺 **设备状态与耗材监测**\n- 📖 知识库检索 (RAG)\n- 🌤️ 城市天气与气象预警\n- 🌬️ 空气质量分析\n- 📊 外部历史数据对比")

# 页面标题和描述
st.title("✨ Vacuum Agent 智能管家")
st.markdown("你好！我是您的**专属数字管家**。我不仅能为您解答选购和维护问题，还能**实时监测您家中扫地机器人的状态，并直接执行清扫指令**！")

# 初始化 Agent 实例 (存入 session_state 以避免重复初始化)
if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 渲染历史对话
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("thoughts"):
            # 使用 expander 优雅地展示思考过程
            with st.expander("🧠 查看管家的思考与工具调用过程", expanded=False):
                for thought in message["thoughts"]:
                    if not isinstance(thought, dict):
                        continue
                    st.markdown(f"**Thought:**\n{thought.get('thought', '')}")
                    if thought.get("tool"):
                        st.markdown(f"🛠️ **Tool:** `{thought.get('tool')}`\n- **Input:** `{thought.get('tool_input', '')}`")
                    if thought.get("observation"):
                        st.markdown(f"👁️ **Observation:**\n```\n{thought.get('observation')}\n```")
                    st.markdown("---")
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题，例如：扫地机器人日常如何保养？"):
    # 将用户输入添加到历史并展示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 获取AI响应并解析出思考过程和最终回答
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 调用底层的 stream 方法来捕获所有中间事件
                thoughts_data = []
                final_output = "抱歉，我遇到了一些问题，未能生成完整回答。"
                
                # 构造输入
                input_dict = {
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                # 使用 stream 获取完整的执行过程（包括工具调用和结果）
                # 这里假设底层是基于 langgraph 的 Agent，支持 stream
                for event in st.session_state.agent.agent.stream(input_dict, stream_mode="values", context={"report": False}):
                    if "messages" in event:
                        latest_msg = event["messages"][-1]
                        
                        # 记录最终的 AIMessage
                        if latest_msg.type == "ai" and latest_msg.content:
                            final_output = latest_msg.content
                            
                        # 捕获工具调用 (Thought & Tool)
                        if hasattr(latest_msg, "tool_calls") and latest_msg.tool_calls:
                            for tc in latest_msg.tool_calls:
                                if not tc: continue
                                # 尝试从消息的 content 中提取 Thought，如果没有则使用默认文本
                                thought_text = latest_msg.content.strip() if isinstance(latest_msg.content, str) and latest_msg.content else f"决定调用工具：{tc.get('name', 'Unknown') if isinstance(tc, dict) else getattr(tc, 'name', 'Unknown')}"
                                
                                # 处理不同格式的 ToolCall
                                tool_name = tc.get("name", "Unknown") if isinstance(tc, dict) else getattr(tc, "name", "Unknown")
                                tool_args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
                                
                                thoughts_data.append({
                                    "thought": thought_text,
                                    "tool": tool_name,
                                    "tool_input": str(tool_args),
                                    "observation": "" # 等待下一个 ToolMessage 补充
                                })
                                
                        # 捕获工具执行结果 (Observation)
                        if latest_msg.type == "tool":
                            # 找到对应的 thought 记录并补充 observation
                            for t in reversed(thoughts_data):
                                if t["tool"] == latest_msg.name and t["observation"] == "":
                                    obs_str = str(latest_msg.content)
                                    t["observation"] = obs_str[:500] + ("..." if len(obs_str) > 500 else "")
                                    break
                
                # 在界面上展示思考过程
                if thoughts_data:
                    with st.expander("🧠 查看管家的思考与工具调用过程", expanded=False):
                        for thought in thoughts_data:
                            if not isinstance(thought, dict):
                                continue
                            st.markdown(f"**Thought:**\n{thought.get('thought', '')}")
                            if thought.get('tool'):
                                st.markdown(f"🛠️ **Tool:** `{thought.get('tool')}`\n- **Input:** `{thought.get('tool_input', '')}`")
                            if thought.get('observation'):
                                st.markdown(f"👁️ **Observation:**\n```\n{thought.get('observation')}\n```")
                            st.markdown("---")
                            
                st.markdown(final_output)
                
                # 存入历史记录
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_output,
                    "thoughts": thoughts_data
                })

            except Exception as e:
                error_msg = f"发生错误: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
