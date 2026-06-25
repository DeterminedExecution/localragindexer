// Tiny web site: serves index.html and one /ask endpoint backed by the RAG chain.
import { answer } from "./rag";

const server = Bun.serve({
  port: 8000,
  hostname: "127.0.0.1",
  async fetch(req) {
    const url = new URL(req.url);
    if (req.method === "POST" && url.pathname === "/ask") {
      const { question, history, diagnostics } = await req.json();
      return Response.json(await answer(question, history ?? [], !!diagnostics));
    }
    return new Response(Bun.file("index.html"), {
      headers: { "Content-Type": "text/html", "Cache-Control": "no-store" },
    });
  },
});

console.log(`Harrier RAG running at http://${server.hostname}:${server.port}`);
