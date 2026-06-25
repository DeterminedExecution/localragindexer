/**
 * Basic langchain RAG over the Harrier corpus — straight out of the LCEL examples.
 *
 * Online provider only (OpenAI: one key does both chat + embeddings). The whole
 * pipeline is the four canonical steps: load -> index -> retrieve -> generate.
 *
 * To upgrade later, replace ONLY the retriever in the marked block below
 * (graphrag / lightrag / etc.); the chain around it stays the same.
 */
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { Document } from "@langchain/core/documents";
import { MemoryVectorStore } from "@langchain/classic/vectorstores/memory";
import { ChatPromptTemplate, MessagesPlaceholder } from "@langchain/core/prompts";
import { HumanMessage, AIMessage, type BaseMessage } from "@langchain/core/messages";
import { StringOutputParser } from "@langchain/core/output_parsers";

// 1. Load documents
const lines = (await Bun.file("data/harrier.jsonl").text()).trim().split("\n");
const docs = lines.map((line) => {
  const o = JSON.parse(line);
  return new Document({
    pageContent: o.text,
    metadata: { doc_id: o.doc_id, title: o.title, page: o.page, url: o.url },
  });
});

// ---- retrieval (swap this block for graphrag / lightrag later) ----
// 2. Index   3. Retrieve
const vectorStore = await MemoryVectorStore.fromDocuments(docs, new OpenAIEmbeddings());
const retriever = vectorStore.asRetriever(4);
// -------------------------------------------------------------------

// 4. Generate
const llm = new ChatOpenAI({ model: "gpt-4o-mini", temperature: 0 });

// History-aware retrieval: rephrase a follow-up into a standalone search query.
const contextualize = ChatPromptTemplate.fromMessages([
  [
    "system",
    "Given the chat history and the latest user question, rephrase it into a standalone " +
      "question understandable without the history. Do NOT answer it — only reformulate, " +
      "or return it unchanged if it is already standalone.",
  ],
  new MessagesPlaceholder("history"),
  ["human", "{question}"],
])
  .pipe(llm)
  .pipe(new StringOutputParser());

// Answer using the chat history + the retrieved context.
const generate = ChatPromptTemplate.fromMessages([
  [
    "system",
    "You are a research assistant for the AV-8 / Harrier. Answer using only the context " +
      "below. Cite sources as [doc_id p.page]. If the context lacks the answer, say so.\n\n" +
      "Context:\n{context}",
  ],
  new MessagesPlaceholder("history"),
  ["human", "{question}"],
])
  .pipe(llm)
  .pipe(new StringOutputParser());

// Collapse the per-word newlines left over from PDF text extraction into flowing prose.
const clean = (s: string) => s.replace(/\s+/g, " ").trim();
const formatDocs = (docs: Document[]) =>
  docs.map((d) => `[${d.metadata.doc_id} p.${d.metadata.page}] ${clean(d.pageContent)}`).join("\n\n");

export interface Source {
  doc_id: string;
  title: string;
  page: number;
  url: string; // deep-linked to the exact PDF page via #page=N
}

export interface Turn {
  role: "user" | "assistant";
  content: string;
}

export async function answer(question: string, history: Turn[] = [], diagnostics = false) {
  const messages: BaseMessage[] = history.map((m) =>
    m.role === "user" ? new HumanMessage(m.content) : new AIMessage(m.content),
  );

  // condense follow-ups into a standalone query (the first turn needs no rewrite)
  const searchQuery = messages.length ? await contextualize.invoke({ history: messages, question }) : question;
  const docs = await retriever.invoke(searchQuery); // retrieve
  const context = formatDocs(docs); // the RAG block inserted into the prompt
  const text = await generate.invoke({ context, history: messages, question }); // generate

  // one link per distinct doc+page, each opening the PDF at the right page
  const sources: Source[] = [];
  const seen = new Set<string>();
  for (const d of docs) {
    const m = d.metadata;
    const key = `${m.doc_id}#${m.page}`;
    if (seen.has(key)) continue;
    seen.add(key);
    sources.push({ doc_id: m.doc_id, title: m.title, page: m.page, url: `${m.url}#page=${m.page}` });
  }

  return diagnostics
    ? { answer: text, sources, diagnostics: { query: searchQuery, context } }
    : { answer: text, sources };
}

// Run from the terminal: bun run rag.ts "what is the harrier's empty weight?"
if (import.meta.main) {
  const res = await answer(Bun.argv.slice(2).join(" ") || "What is the Harrier's empty weight?");
  console.log(res.answer + "\n\nSources:");
  for (const s of res.sources) console.log(`  ${s.doc_id} p.${s.page}  ${s.url}`);
}
