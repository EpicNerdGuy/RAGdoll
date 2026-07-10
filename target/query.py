from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTORSTORE_PATH
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import Chroma

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

vectorstore = Chroma(
    persist_directory=VECTORSTORE_PATH,
    embedding_function=embeddings
)

