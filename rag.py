"""LightRAG core for localragindexer (Project #2 of 3).

Graph RAG over a PDF corpus: the index is a knowledge graph (entities + relationships)
plus a vector store; queries use LightRAG's graph-aware retrieval.

Works standalone with OpenAI. To run fully offline with Project #3 (localragllm),
flip PROVIDER to "local" below and rebuild the index once (python index_corpus.py).
"""
import os
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

# ======================= CONFIG — switch provider here =======================
PROVIDER = "openai"            # "openai" (cloud, needs OPENAI_API_KEY) | "local" (Project #3 / Ollama, offline)
LOCAL_MODEL = "qwen2.5:7b"     # used when PROVIDER == "local"  (or "llama3.2:3b" on low-RAM machines)
OLLAMA_HOST = "http://localhost:11434"
# =============================================================================

HERE = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.join(HERE, "rag_storage")  # persisted graph + vectors

# Where Project #1 (localragdownloader) saves its PDFs. Cloned as siblings this default
# "just works"; otherwise point it at your folder (env PDFS_DIR overrides, or pass
# --pdfs <dir> to index_corpus.py).
PDFS_DIR = os.environ.get("PDFS_DIR", os.path.normpath(os.path.join(HERE, "..", "localragdownloader", "pdfs")))


def load_env():
    """Minimal .env loader (no dependency); shell env still wins."""
    envp = os.path.join(HERE, ".env")
    if os.path.exists(envp):
        for line in open(envp):
            line = line.strip()
            if line.startswith("OPENAI_API_KEY=") and not os.environ.get("OPENAI_API_KEY"):
                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1]


def _build_lightrag() -> LightRAG:
    if PROVIDER == "local":
        # fully offline via Ollama's OpenAI-compatible API (Project #3) — nomic embeddings (768-dim).
        # Raw embedding call avoids LightRAG's openai_embed/ollama_embed hardcoded-dim wrappers.
        import numpy as np
        from openai import AsyncOpenAI
        from lightrag.llm.openai import openai_complete_if_cache
        base = OLLAMA_HOST + "/v1"
        client = AsyncOpenAI(base_url=base, api_key="ollama")

        async def _local_llm(prompt, system_prompt=None, history_messages=[], **kwargs):
            return await openai_complete_if_cache(
                LOCAL_MODEL, prompt, system_prompt=system_prompt,
                history_messages=history_messages, base_url=base, api_key="ollama", **kwargs)

        async def _local_embed(texts):
            resp = await client.embeddings.create(model="nomic-embed-text", input=texts)
            return np.array([d.embedding for d in resp.data])

        return LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=_local_llm,
            embedding_func=EmbeddingFunc(embedding_dim=768, max_token_size=8192, func=_local_embed),
        )
    # default: OpenAI (cloud) — 1536-dim embeddings
    from lightrag.llm.openai import gpt_4o_mini_complete, openai_embed
    load_env()
    return LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=gpt_4o_mini_complete,
        embedding_func=EmbeddingFunc(
            embedding_dim=1536,
            max_token_size=8192,
            func=lambda texts: openai_embed(texts, model="text-embedding-3-small"),
        ),
    )


async def get_rag() -> LightRAG:
    os.makedirs(WORKING_DIR, exist_ok=True)
    rag = _build_lightrag()
    await rag.initialize_storages()
    await initialize_pipeline_status()
    return rag


async def answer(rag: LightRAG, question: str, history=None, diagnostics: bool = False) -> dict:
    """One conversational, graph-aware query. Returns {answer, sources, diagnostics?}."""
    conv = [{"role": m["role"], "content": m["content"]} for m in (history or [])]
    param = QueryParam(
        mode="hybrid",              # graph (entities+relations) + vector
        include_references=True,    # citation markers -> PDF source links
        enable_rerank=False,
        conversation_history=conv,  # the dialog
    )
    text = await rag.aquery(question, param=param)

    out = {"answer": text, "sources": _extract_sources(text)}
    if diagnostics:
        ctx = await rag.aquery(question, param=QueryParam(
            mode="hybrid", only_need_context=True, enable_rerank=False, conversation_history=conv))
        out["diagnostics"] = {"query": question, "context": ctx}
    return out


def _extract_sources(text: str):
    """Turn LightRAG's `DOCID.pdf#page=N` citations into clickable archive.org page links."""
    import re
    seen, sources = set(), []
    for m in re.finditer(r"([A-Za-z0-9][\w.\-]*)\.pdf#page=(\d+)", text):
        doc_id, page = m.group(1), int(m.group(2))
        if (doc_id, page) in seen:
            continue
        seen.add((doc_id, page))
        sources.append({
            "doc_id": doc_id,
            "title": doc_id,
            "page": page,
            "url": f"https://archive.org/download/{doc_id}/{doc_id}.pdf#page={page}",
        })
    return sources
