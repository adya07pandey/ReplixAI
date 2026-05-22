import os

from sqlalchemy.orm import Session
from sqlalchemy import text

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.database.models import PolicyEmbedding


embeddings_model = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=os.getenv("HF_API_KEY"),
    model="sentence-transformers/all-MiniLM-L6-v2"
)

def chunk_text(text, chunk_size=400, overlap=80):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(text[start:end])

        start += chunk_size - overlap

    return chunks


def store_policy(
    db: Session,
    org_id: int,
    text_data: str
):

    db.query(PolicyEmbedding).filter(
        PolicyEmbedding.org_id == org_id
    ).delete()

    chunks = chunk_text(text_data)

    embeddings = embeddings_model.embed_documents(chunks)

    for chunk, embedding in zip(chunks, embeddings):

        row = PolicyEmbedding(
            org_id=org_id,
            chunk_text=chunk,
            embedding=embedding
        )

        db.add(row)

    db.commit()

    print(f"Stored {len(chunks)} chunks")

def retrieve_context(
    db: Session,
    org_id: int,
    query: str,
    k: int = 3
):

    query_embedding = embeddings_model.embed_query(query)

    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text(
        """
        SELECT chunk_text
        FROM policy_embeddings
        WHERE org_id = :org_id
        ORDER BY embedding <=> CAST(:embedding AS vector)
        LIMIT :k
        """
    )

    results = db.execute(
        sql,
        {
            "org_id": org_id,
            "embedding": embedding_str,
            "k": k
        }
    ).fetchall()

    return "\n\n".join([r[0] for r in results])