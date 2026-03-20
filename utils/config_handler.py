import yaml
from utils.path_tool import get_abs_path


# 配置加载工具：读取并解析 RAG 的 YAML 配置文件。
def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8"):
    # 按指定编码打开 YAML 配置文件。
    with open(config_path, "r", encoding=encoding) as f:
        # 使用 FullLoader 将 YAML 内容反序列化为 Python 数据结构（如 dict/list）。
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    # 按指定编码打开 YAML 配置文件。
    with open(config_path, "r", encoding=encoding) as f:
        # 使用 FullLoader 将 YAML 内容反序列化为 Python 数据结构（如 dict/list）。
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    # 按指定编码打开 YAML 配置文件。
    with open(config_path, "r", encoding=encoding) as f:
        # 使用 FullLoader 将 YAML 内容反序列化为 Python 数据结构（如 dict/list）。
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    # 按指定编码打开 YAML 配置文件。
    with open(config_path, "r", encoding=encoding) as f:
        # 使用 FullLoader 将 YAML 内容反序列化为 Python 数据结构（如 dict/list）。
        return yaml.load(f, Loader=yaml.FullLoader)


def load_weather_config(config_path: str = get_abs_path("config/weather.yml"), encoding: str = "utf-8"):
    # 按指定编码打开 YAML 配置文件。
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()
weather_conf = load_weather_config()
