"""Build the LightRAG knowledge graph. Run once:

    python index_corpus.py               # bundled sample corpus (data/harrier.jsonl)
    python index_corpus.py --pdfs        # ingest Project 1's PDFs (sibling localragdownloader/pdfs)
    python index_corpus.py --pdfs DIR    # ingest a specific PDF folder

Each page is tagged with its archive.org deep link as its source, so citations resolve
straight to the right page. Persists to rag_storage/ (reused by the server).
"""
import os
import glob
import json
import argparse
import asyncio

from rag import get_rag, PDFS_DIR


def load_jsonl(path):
    texts, paths = [], []
    for line in open(path):
        o = json.loads(line)
        texts.append(o["text"])
        paths.append(f'{o["url"]}#page={o["page"]}')
    return texts, paths


def load_pdfs(pdf_dir):
    """Read a directory of PDFs (e.g. produced by localragdownloader / Project 1)."""
    from pypdf import PdfReader
    texts, paths = [], []
    for pdf in sorted(glob.glob(os.path.join(pdf_dir, "*.pdf"))):
        name = os.path.basename(pdf)[:-4]
        try:
            reader = PdfReader(pdf)
        except Exception as e:
            print(f"  skip {name}: {e}")
            continue
        for i, page in enumerate(reader.pages, 1):
            t = (page.extract_text() or "").strip()
            if len(t) < 40:
                continue
            texts.append(t)
            # Project 1's filenames are archive.org identifiers -> rebuild the page deep link
            paths.append(f"https://archive.org/download/{name}/{name}.pdf#page={i}")
    return texts, paths


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdfs", nargs="?", const=PDFS_DIR, default=None,
                    help=f"ingest PDFs from a directory; flag alone uses Project 1's folder ({PDFS_DIR})")
    ap.add_argument("--corpus", default="data/harrier.jsonl", help="bundled jsonl corpus")
    args = ap.parse_args()

    rag = await get_rag()
    if args.pdfs:
        texts, paths = load_pdfs(args.pdfs)
        print(f"ingesting {len(texts)} pages from PDFs in {args.pdfs} -> building graph…", flush=True)
    else:
        texts, paths = load_jsonl(args.corpus)
        print(f"ingesting {len(texts)} chunks from {args.corpus} -> building graph…", flush=True)

    await rag.ainsert(texts, file_paths=paths)
    print("done. knowledge graph + vectors persisted to rag_storage/")


if __name__ == "__main__":
    asyncio.run(main())
