from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTORSTORE_PATH, LLM_MODEL, TOP_K
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma

def build_chain():
    embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory = VECTORSTORE_PATH,
        embedding_function = embeddings
    )
    
    print(f"Loaded {vectorstore._collection.count()} chunks from vectorstore at {VECTORSTORE_PATH}")
    llm = Ollama(model = LLM_MODEL)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm = llm,
        retiriever = vectorstore.as_retriever(search_kwargs = {"k": TOP_K}),
    )
    
    return qa_chain

def ask(question):
    qa_chain = build_chain()
    return qa_chain.run(question)

if __name__ == "__main__":
    question = input("Enter your question: ")
    answer = ask(question)
    print(answer)
    


