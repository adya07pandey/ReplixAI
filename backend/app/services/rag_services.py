from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from qdrant_client.models import Filter, FieldCondition, MatchValue,PayloadSchemaType
import os
import uuid

model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

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

def chunk_text(text, chunk_size=400, overlap=80):

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks

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
    embeddings = model.encode(chunks)

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={"text": chunk}
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]

    qdrant.upsert(collection_name=collection_name, points=points)

    print(f"Stored {len(points)} chunks for org {org_id}")


def retrieve_context(org_id, query, k=3):
    collection_name = get_collection_name(org_id)

    query_vector = model.encode(query).tolist()

    results = qdrant.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=k
    )

    return "\n\n".join([point.payload["text"] for point in results.points])

