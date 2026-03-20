from abc import ABC, abstractmethod
from typing import Optional
from utils.config_handler import rag_conf
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel, ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(selfs) -> Optional[Embeddings | BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> BaseChatModel:
        return ChatTongyi(
            model=rag_conf["chat_model_name"],
            dashscope_api_key=rag_conf["embedding_dashscope_api_key"],
        )


class EmbeddingFactory(BaseModelFactory):
    def generator(self) -> Embeddings:
        return DashScopeEmbeddings(
            model=rag_conf["embedding_model_name"],
            dashscope_api_key=rag_conf["embedding_dashscope_api_key"],
        )


chat_model = ChatModelFactory().generator()
embedding_model = EmbeddingFactory().generator()