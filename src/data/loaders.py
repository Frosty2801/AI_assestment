"""Document loaders and chunkers."""
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import os


def load_documents(path: str = "../data/documents") -> list[Document]:
    """Load all MD/TXT files from directory."""
    loader = DirectoryLoader(
        path,
        glob="**/*.md",
        loader_cls=TextLoader,
        show_progress=True
    )
    return loader.load()


def split_documents(docs: list[Document], chunk_size: int = 512, chunk_overlap: int = 100) -> list[Document]:
    """Chunk with overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(docs)
