from langchain_core.tools import tool
from tavily import TavilyClient
import os
from utils.logger_handler import logger
from utils.config_handler import agent_conf

# 尝试从配置文件或环境变量获取 API Key
TAVILY_API_KEY = agent_conf.get("tavily_api_key") or os.environ.get("TAVILY_API_KEY", "")

@tool(description="一个专门用于Web搜索的工具。当你需要从互联网上搜索最新的信息、新闻或任何未知知识时，请使用此工具。")
def web_search(query: str) -> str:
    """使用 Tavily 进行 Web 搜索"""
    if not TAVILY_API_KEY:
        error_msg = "Tavily API Key 未配置，请在 config/agent.yml 中或通过环境变量 TAVILY_API_KEY 进行配置。"
        logger.error(f"[TavilyTool] {error_msg}")
        return error_msg
        
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        # 执行搜索，可以根据需要调整参数，比如 search_depth="advanced"
        response = client.search(query=query, search_depth="basic")
        
        # 提取并格式化搜索结果
        results = response.get("results", [])
        if not results:
            return f"未能找到关于 '{query}' 的搜索结果。"
            
        formatted_results = f"【'{query}' 的 Web 搜索结果】\n"
        for idx, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            content = result.get("content", "无内容")
            url = result.get("url", "无链接")
            formatted_results += f"{idx}. {title}\n   摘要: {content}\n   来源: {url}\n\n"
            
        return formatted_results
    except Exception as e:
        logger.error(f"[TavilyTool] Web搜索失败: {e}")
        return f"执行Web搜索时发生错误，请稍后再试。"
