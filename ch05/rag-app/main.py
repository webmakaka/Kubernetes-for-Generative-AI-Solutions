# Standard Library imports
import uuid
import os
import io
import csv
import logging
import traceback

# Third-party libraries
import httpx
import boto3

# FastAPI and Pydantic imports
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Langchain Components
from langchain.chains import RetrievalQA, create_history_aware_retriever, create_retrieval_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain.chains.combine_documents import create_stuff_documents_chain

# Qdrant Client Integration
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore

# Community Add-ons and Utilities
from langchain_community.chat_message_histories import ChatMessageHistory

# Core components for prompts
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# OpenAI Integrations
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Langsmith Tracing
from langsmith import traceable

# Setup logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Hold user sessions (Consider using Redis or a persistent store for scalability)
user_sessions = {}

# Fetch Qdrant endpoint from environment variables
QDRANT_ENDPOINT = os.getenv("QDRANT_ENDPOINT", "http://localhost:6333")

try:
    # Set up Qdrant client with proper error handling
    qdrant_client = QdrantClient(url=QDRANT_ENDPOINT)
    collection_name = "catalog"
    logger.info("Successfully connected to Qdrant at %s", QDRANT_ENDPOINT)
except Exception as e:
    logger.error("Failed to connect to Qdrant: %s", e)
    raise

# Define the request body schema
class PromptModel(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class LoadDataModel(BaseModel):
    url: str

# FastAPI app instance
app = FastAPI()

@app.post("/load_data")
async def load_data(request: LoadDataModel):
    try:
        # Fetch the file from the input URL using async HTTP client
        async with httpx.AsyncClient() as client:
            response = await client.get(request.url)
        
        # Handle non-200 status codes
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to download file from the URL")
        
        # Convert the content of the response to a BytesIO object and then a string
        file_content = io.StringIO(response.text)

        # Load the CSV file using the built-in csv module
        reader = csv.DictReader(file_content)

        # Convert the CSV rows to text documents
        documents = []
        for row in reader:
            doc_content = "\n".join([f"{key}: {value}" for key, value in row.items()])
            documents.append(Document(page_content=doc_content))

        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = text_splitter.split_documents(documents)
        
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)  # Vector size set to 256
        )
        
        embeddings = OpenAIEmbeddings()
        
        qdrant_store = QdrantVectorStore(
            embedding=embeddings, 
            collection_name=collection_name, 
            client=qdrant_client
        )
        qdrant_store.add_documents(docs)
        
        return JSONResponse({"message": "Document ingested successfully!"}, status_code=200)

    except httpx.HTTPStatusError as e:
        logger.error("HTTP Error occurred while downloading the file: %s", e)
        raise HTTPException(status_code=500, detail="Failed to download the file")

    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while loading data")



def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in user_sessions:
        user_sessions[session_id] = ChatMessageHistory()
    return user_sessions[session_id]
    

@app.post("/generate")
@traceable()
async def generate_answer(prompt_model: PromptModel):
    try:
        prompt = prompt_model.prompt
        session_id = prompt_model.session_id

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        # If no session ID is provided, create a new session
        if not session_id:
            session_id = str(uuid.uuid4())
                
                
        ### Contextualize question ###
        contextualize_q_system_prompt = (
            "Given a chat history and the latest user question "
            "which might reference context in the chat history, "
            "formulate a standalone question which can be understood "
            "without the chat history. Do NOT answer the question, "
            "just reformulate it if needed and otherwise return it as is."
        )
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        embeddings = OpenAIEmbeddings()
        
        qdrant_store = QdrantVectorStore(
            embedding=embeddings, 
            collection_name=collection_name, 
            client=qdrant_client
        )
        
        history_aware_retriever = create_history_aware_retriever(
            llm, qdrant_store.as_retriever(), contextualize_q_prompt
        )
        
        ### Answer question ###
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use 3 to 5 sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
        
        result = conversational_rag_chain.invoke(
            {"input": prompt},
            config={"configurable": {"session_id": session_id}},
        )["answer"]

        
        print (result)

        return JSONResponse({"response": result, "session_id": session_id}, status_code=200)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
