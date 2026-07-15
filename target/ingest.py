from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTORSTORE_PATH

loader = TextLoader("target/docs/clean/steins_gate_summary.txt", encoding="utf-8")
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = CHUNK_SIZE,
    chunk_overlap = CHUNK_OVERLAP
)
chunks = text_splitter.split_documents(documents)

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore = Chroma.from_documents(
    documents = chunks,
    embedding = embeddings,
    persist_directory = VECTORSTORE_PATH
)




