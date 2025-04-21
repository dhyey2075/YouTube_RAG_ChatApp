import streamlit as st

from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from qdrant_client.http.models import Distance, VectorParams
from langchain.docstore.document import Document
from qdrant_client.http.models import Filter, FieldCondition, MatchValue


import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(
    url=st.secrets["QDRANT_URL"], 
    api_key=st.secrets["QDRANT_API_KEY"]
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=st.secrets["GOOGLE_API_KEY"])


vector_store = QdrantVectorStore(
    client=client,
    collection_name="youtube-transcripts",
    embedding=embeddings,
)


st.title("YouTube Chat App")

st.subheader("Enter a YouTube video URL to get the chat messages.")


video_url = st.text_input("Label", label_visibility="collapsed", placeholder="Enter YouTube video URL")

if video_url:
    st.write(f"You entered: {video_url}")
    try:
        loader = YoutubeLoader.from_youtube_url(
            video_url,
            add_video_info=False,
            language=["en", "hi"],
            translation="en",
        )

        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(docs)

        for i, doc in enumerate(chunks):
            doc.metadata["id"] = str(i)

        # Add documents to the vector store
        vector_store.add_documents(documents=chunks)

        st.success("Documents added to the vector store!")
    except Exception as e:
        st.error(f"Error: {e}")

prompt = st.chat_input("Ask a question about the video:")
if prompt:
    st.write(f"You asked: {prompt}")
    try:
        results = vector_store.similarity_search(prompt, k=5)

        # Start the chat loop
        while True:
            query = prompt
            if query.lower() == "exit":
                break

            chat = ChatGroq(temperature=0.5, groq_api_key = st.secrets["GROQ_API_KEY"], model_name="gemma2-9b-it")

            context = "\n".join([doc.page_content for doc in results])
            
            system_prompt = "You are a helpful assistant who solves user queries based on the provided context: {context}"

            # Create the ChatPromptTemplate with placeholders for context and user input
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{user_input}")
            ])

            # Format the prompt with the current context and user query
            formatted_messages = prompt.format_messages(context=context, user_input=query)

            formatted_prompt = "\n".join([message.content for message in formatted_messages])

            # Invoke the chat model with the formatted prompt
            response = chat.invoke(formatted_prompt)

            st.markdown(f"Response: {response.to_json()['kwargs']['content']}")

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Clear"):
    filter_all = Filter(must=[])

    client.delete(
        collection_name="youtube-transcripts",
        points_selector=filter_all
    )

