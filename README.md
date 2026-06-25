# Harrier RAG

A deliberately minimal [langchain](https://js.langchain.com) RAG over a Harrier /
AV-8 document corpus, with a one-page web UI. The whole pipeline is the four canonical
steps — load → index → retrieve → generate — in one short file ([`rag.ts`](rag.ts)).

TypeScript on [Bun](https://bun.sh): no build step, native `.env` loading, and a
built-in HTTP server, so the only dependencies are the three `@langchain/*` packages.
Online provider only — **OpenAI** supplies both the chat model and the embeddings.

## Run

```bash
bun install
cp .env.example .env          # add your OPENAI_API_KEY
bun start                     # open http://127.0.0.1:8000
```

Or from the terminal: `bun run rag.ts "what is the harrier's empty weight?"`

## Files

| File | What |
|------|------|
| `rag.ts` | the entire RAG chain (load → index → retrieve → generate) |
| `server.ts` | the web server: serves the page + `/ask` (`Bun.serve`) |
| `index.html` | the web UI |
| `data/harrier.jsonl` | the document corpus (1,203 Harrier passages) |

## Swapping the retriever (graphrag / lightrag / …)

The retriever is isolated in one marked block in `rag.ts`:

```ts
// ---- retrieval (swap this block for graphrag / lightrag later) ----
const vectorStore = await MemoryVectorStore.fromDocuments(docs, new OpenAIEmbeddings());
const retriever = vectorStore.asRetriever(4);
// -------------------------------------------------------------------
```

Replace those two lines with any retriever; the surrounding chain is unchanged.
