"""Web server for localragindexer (Project #2): serves the chat UI + /ask, backed by LightRAG.

The knowledge graph is built once by `index_corpus.py`; this just loads it and queries.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from rag import get_rag, answer

rag = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag
    rag = await get_rag()  # load the prebuilt graph from rag_storage/ (no rebuild)
    yield


app = FastAPI(lifespan=lifespan)


class Ask(BaseModel):
    question: str
    history: list = []
    diagnostics: bool = False


@app.get("/")
def home():
    return FileResponse("index.html", headers={"Cache-Control": "no-store"})


@app.post("/ask")
async def ask(body: Ask):
    return await answer(rag, body.question, body.history, body.diagnostics)
