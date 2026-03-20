from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger


def load_system_prompts():
    try:
        system_prompt_path = get_abs_path(prompts_conf["main_prompt_path"])

    except KeyError as e:
        logger.error(f"[load_system_prompt] 配置文件缺少 main_prompt_path 配置")
        raise e

    try:
        return open(system_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_system_prompt] 解析系统提示词出错，{str(e)}")
        raise e


def load_rag_prompt():
    try:
        rag_prompt_path = get_abs_path(prompts_conf["rag_summarize_prompt"])

    except KeyError as e:
        logger.error(f"[load_rag_prompt] 配置文件缺少 rag_summarize_prompt 配置")
        raise e

    try:
        return open(rag_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_prompt] 解析RAG总结提示词出错，{str(e)}")
        raise e


def load_report_prompt():
    try:
        report_prompt_path = get_abs_path(prompts_conf["report_prompt_path"])

    except KeyError as e:
        logger.error(f"[load_report_prompt] 配置文件缺少 report_prompt_path 配置")
        raise e

    try:
        return open(report_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_report_prompt] 解析报告生成提示词出错，{str(e)}")
        raise e
