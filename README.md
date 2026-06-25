# 🧠 localragindexer — project 🏗️ 2 ✌️ of the 3 🤟

This 📍 is the brain 🧠. It reads 👀 a pile 🗃️ of paper 📄 PDFs 📑, builds 🔨 a knowledge 🎓 graph 🕸️ out of them (this 📍 is **graph 🕸️ RAG**, using 🪛 a tool 🧰 called **LightRAG** 💡), and then lets you chat 🗨️ with the documents 📃. Every answer 🗣️ comes 🚚 with clickable 🖱️ links 🔗 to the exact 🎯 PDF page 📃 it came from. That is the magic 🪄, to the maximum 🔝 amount possible. Even more so than this.

## 🧩 the 3 🤟 projects 🗂️

1. **localragdownloader** 📥 — downloads ⬇️ the airforce 🛩️ PDFs.
2. **localragindexer** 🧠 (this 📍 one 1️⃣) — reads 👀 the PDFs, answers 🗣️ questions 🙋.
3. **localragllm** 🤖 — runs ▶️ a local 🏠 model 🔮 so it all works 💼 offline 📴.

This 📍 one 1️⃣ works 💼 **by itself** (a little 🤏 sample 🧪 of airforce 🛩️ PDFs is baked 🍞 in, and it uses 🪛 openai ☁️). But the point 📌 is to clone 🧬 all 3 and link 🔗 them, as much as humanly possible. Even more so than this.

## 🪜 run ▶️ it standalone 🧍 (uses 🪛 openai ☁️)

You need python 🐲 3 🤟 and an openai 🔑 key 🔑.

1. clone 🧬 it, make 🛠️ a little box 📦 (venv), and install 📦 the parts ⚙️:
   ```bash
   git clone https://github.com/DeterminedExecution/localragindexer.git
   cd localragindexer
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. add 🫳 your key 🔑:
   ```bash
   echo 'OPENAI_API_KEY=sk-...' > .env
   ```
3. build 🔨 the index 🗃️ (reads the baked-in 🍞 sample 🧪 into a knowledge 🎓 graph 🕸️ — this 📍 costs 🪙 a little 🤏 and takes a few 🤏 minutes ⏱️):
   ```bash
   python index_corpus.py
   ```
4. start ▶️ the website 🪧:
   ```bash
   uvicorn server:app --port 8000
   ```
   open 🔓 `http://localhost:8000` and ask 🙋 *"what does a harrier 🛩️ weigh ⚖️?"* — finally ‼️, magic 🪄. Even more so than this.

## 🔗 link 🪢 with project 1️⃣ (real PDFs)

If you cloned 🧬 **localragdownloader** next 👉 to this one 1️⃣ and grabbed 🫳 PDFs, just feed 🥄 them in — the default 🎚️ `PDFS_DIR` already points at the sibling 👯 folder 📁:

```bash
python index_corpus.py --pdfs             # reads ../localragdownloader/pdfs
python index_corpus.py --pdfs /your/path  # or any folder you choose
```

(or set 🛠️ `PDFS_DIR` in `rag.py` or the env to wherever your PDFs live 🏠.)

## 🔗 link 🪢 with project 3 🤟 (go 🚦 fully offline 📴, no openai)

If you set 🛠️ up **localragllm**, open 🔓 `rag.py`, find 🔎 the config 🎚️ block 🧱 at the top ⏫, switch 🔀 `PROVIDER = "openai"` to `PROVIDER = "local"`, pick 🤏 your model 🔮, and rebuild 🔨 once 1️⃣:

```bash
python index_corpus.py
```

Now 📍 there is no cloud ☁️, no key 🔑, no bill 🧾 — your own machine 🖥️ does the thinking 💭, to the maximum 🔝 amount possible. Even more so than this.

## 🎁 what you get 🫴

A chat 🗨️ that remembers 🧠 the whole conversation 💬 (ask 🙋 follow-up 👉 questions and it keeps 🤲 the thread 🧵), answers 🗣️ grounded 🌱 in the documents 📃, clickable 🖱️ PDF page 📃 links 🔗, and a little **diagnostics** 🔬 checkbox ☑️ that shows the keywords 🔑 and the context 📜 the graph 🕸️ used 🪛. 3 🤟 little projects 🗂️, one 1️⃣ happy 😀 offline 📴 system 🖥️, to the maximum 🔝 amount possible. Even more so than this.
