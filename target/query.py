from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, VECTORSTORE_PATH, LLM_MODEL, TOP_K
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

def build_chain():
    embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL)
    vectorstore = Chroma(
        persist_directory = VECTORSTORE_PATH,
        embedding_function = embeddings
    )
    llm = Ollama(model = LLM_MODEL)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    
    system_prompt = (
        "Use the given context to answer the question. "
        "If you don't know the answer, say you don't know.\n\n"
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)

    return rag_chain

def ask(question):
    qa_chain = build_chain()
    return qa_chain.invoke({"input": question})

if __name__ == "__main__":
    question = input("Enter your question: ")
    answer = ask(question)
    print(answer)
    


