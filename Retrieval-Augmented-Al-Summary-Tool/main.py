import os
import streamlit as st
import time
from langchain.llms import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

st.title("News Research Tool 📈")
st.sidebar.title("News Article URL")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")

# Change: Save folder instead of pickle
FAISS_PATH = "faiss_index_openai"
main_placeholder = st.empty()

llm = OpenAI(temperature=0.9, max_tokens=500)

if process_url_clicked:
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading....Started....✅✅✅✅")
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000,
        chunk_overlap=200
    )
    main_placeholder.text("Text Splitter....Started....✅✅✅✅")

    docs = text_splitter.split_documents(data)

    for i, doc in enumerate(docs):
        if "source" not in doc.metadata:
            doc.metadata["source"] = urls[i % len(urls)] if urls else f"source_{i}"

    embeddings = OpenAIEmbeddings()
    vectorstore_openai = FAISS.from_documents(docs, embeddings)

    main_placeholder.text("Embedding Vector Started Building....✅✅✅✅")
    time.sleep(2)

    vectorstore_openai.save_local(FAISS_PATH)
    main_placeholder.text("FAISS index saved successfully ✅")

query = main_placeholder.text_input("Question:")

if query:
    if os.path.exists(FAISS_PATH):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

        chain = RetrievalQAWithSourcesChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever()
        )

        result = chain({"question": query}, return_only_outputs=True)

        st.header("Answer")
        st.write(result["answer"])

        sources = result.get("sources", "")
        if sources:
            st.subheader("Sources:")
            for source in sources.split("\n"):
                st.write(source)
