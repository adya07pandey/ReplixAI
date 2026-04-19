import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings

# ✅ Use API-based embeddings (NO local model)
embeddings_model = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HF_API_KEY"),
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ✅ Qdrant client
qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)


# 🔹 Collection helpers
def get_collection_name(org_id):
    return f"policies_{org_id}"


def ensure_collection(org_id):
    collection_name = get_collection_name(org_id)

    collections = qdrant.get_collections().collections
    names = [c.name for c in collections]

    if collection_name not in names:
        print(f"Creating collection {collection_name}...")

        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )


# 🔹 Chunking
def chunk_text(text, chunk_size=400, overlap=80):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# 🔹 Store policy
def store_policy(org_id, text):
    collection_name = get_collection_name(org_id)

    try:
        qdrant.delete_collection(collection_name=collection_name)
        print("Old collection deleted")
    except:
        pass

    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        )
    )

    chunks = chunk_text(text)

    print("🔄 Generating embeddings via API...")
    embeddings = embeddings_model.embed_documents(chunks)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk}
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    qdrant.upsert(collection_name=collection_name, points=points)

    print(f"Stored {len(points)} chunks for org {org_id}")


# 🔹 Retrieve context
def retrieve_context(org_id, query, k=3):
    collection_name = get_collection_name(org_id)

    print("🔍 Embedding query via API...")
    query_vector = embeddings_model.embed_query(query)

    results = qdrant.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=k
    )

    return "\n\n".join([point.payload["text"] for point in results.points])