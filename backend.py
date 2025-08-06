from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
app = FastAPI()
llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0.2)
vector = None
qa_chain = None

class TutorRequest(BaseModel):
    subject: str
    level: str
    style: str
    language: str
    question: str

class FollowupRequest(BaseModel):
    question: str

@app.post("/tutor")
def create_tutor_request(request: TutorRequest):
    global vector, qa_chain
    try: 
        prompt = f"""
        You are an AI tutor expert in {request.subject} at {request.level} level with {request.style} learning style in {request.language}. Question: {request.question}

        Provide a clear, structured explanation with examples.
        """

        response = llm.invoke(prompt)
        answer = response.content

        embeddings = OpenAIEmbeddings()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(answer)
        vectorstore = FAISS.from_texts(chunks, embeddings)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, vectorstore=vectorstore, memory=memory)
        
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/ask")
def ask_followup(question: FollowupQuestion):
    global qa_chain
    if not qa_chain:
        raise HTTPException(status_code=400, detail="You must first generate an explanation.")
    
    try:
        result = qa_chain({"question": question.question})
        return {"answer": result["answer"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    