🧩 Natural Language to SQL Assistant for Secure Production Databases
Built a production-grade GenAI system that converts natural language queries into safe SQL SELECT statements using local LLMs (Llama/SQLCoder) for a real-time PostgreSQL database integrated with Django.

- 🧠 Implemented a LangChain-based prompt system using a local LLM (LlamaCpp + SQLCoder) to interpret user queries and dynamically generate context-aware SQL queries.
- 🔐 Enforced SEBI-compliant safety by restricting operations to only SELECT queries, blocking all data modifications, and ensuring schema-safe access to confidential business data.
- 🧱 Handled complex Django MPTT models, foreign key/many-to-many relations, Celery logs, and ORM tables through intelligent schema-aware prompting and query routing.
- 🔌 Integrated psycopg2 for secure query execution, and designed a system architecture that can be deployed securely without requiring OpenAI API keys.
- 🛠️ Engineered embeddings-ready prompt structures for scalable future RAG-based extensions and multi-modal inputs.
- 💻 Technologies: Python, LangChain, LlamaCpp, SQLCoder, PostgreSQL, Django, Hugging Face, Secure Prompt Engineering
