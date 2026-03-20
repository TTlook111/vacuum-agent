from typing import Any


import hashlib
import os
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader


def get_file_hex(file_path: str):  # 获取文件的md5的十六进制字符串

    if not os.path.exists(file_path):
        logger.error(f"[md5计算]文件不存在: {file_path}")
        return

    if not os.path.isfile(file_path):
        logger.error(f"[md5计算]不是文件: {file_path}")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 4KB分片:每次读取文件内容大小
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

            md5_hex = md5_obj.hexdigest()
            return md5_hex
    except Exception as e:
        logger.error(f"[md5计算]文件读取异常: {file_path}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):  # 返回文件夹内的文件列表(允许的文件后缀)
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]: {path}不是文件夹")
        return allowed_types

    for file in os.listdir(path):
        if file.endswith(allowed_types):
            files.append(os.path.join(path, file))

    return tuple[Any, ...](files)


def pdf_loader(file_path: str, passwd=None) -> list[Document]:
    return PyPDFLoader(file_path, passwd).load()


def text_loader(file_path: str) -> list[Document]:
    return TextLoader(file_path, encoding="utf-8", autodetect_encoding=True).load()
