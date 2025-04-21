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


import os
from dotenv import load_dotenv

load_dotenv()

loader = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=ZwS_WlZHnYE",
    add_video_info=False,
    language=["en", "hi"],
    translation="en",
)

docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)


embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

client = QdrantClient(
    url="http://localhost:6333"
)

# First time only
client.create_collection(
    collection_name="youtube-transcripts",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="youtube-transcripts",
    embedding=embeddings,
)
for i, doc in enumerate(chunks):
    doc.metadata["id"] = str(i)

# Add documents to the vector store
vector_store.add_documents(documents=chunks)



# Assuming 'results' is a list of Document objects from your vector store similarity search

# Start the chat loop
while True:
    query = input(">: ")
    if query.lower() == "exit":
        break

    results = vector_store.similarity_search(
        query, k=2
    )

    chat = ChatGroq(temperature=0, groq_api_key = os.getenv("GROQ_API_KEY"), model_name="gemma2-9b-it")

    context = "\n".join([doc.page_content for doc in results])
    
    system_prompt = "You are a helpful assistant who solves user queries based on the provided context: {context}"

    # Create the ChatPromptTemplate with placeholders for context and user input
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_input}")
    ])

    # Format the prompt with the current context and user query
    formatted_prompt = prompt.format(context=context, user_input=query)

    # Invoke the chat model with the formatted prompt
    response = chat.invoke(formatted_prompt)

    # Print the model's response
    print(response.content)