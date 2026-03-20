import boto3
import json
import os
import faiss
import numpy as np
import logging
from io import BytesIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment variables
S3_BUCKET = os.environ["S3_BUCKET"]
VECTOR_FILE_KEY = os.environ["VECTOR_FILE_KEY"]  # e.g., "vectors/doc_vectors.json"

# Global variables
document_texts = []
document_vectors = None
faiss_index = None
index_loaded = False

# AWS clients
s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime")

def load_faiss_from_s3():
    global faiss_index, document_texts, document_vectors, index_loaded

    logger.info(f"Loading FAISS index from s3://{S3_BUCKET}/{VECTOR_FILE_KEY}")

    obj = s3.get_object(Bucket=S3_BUCKET, Key=VECTOR_FILE_KEY)
    data = json.loads(obj["Body"].read().decode("utf-8"))

    document_texts = data["texts"]
    vectors = data["vectors"]
    document_vectors = np.array(vectors).astype("float32")

    faiss_index = faiss.IndexFlatL2(len(document_vectors[0]))
    faiss_index.add(document_vectors)

    index_loaded = True
    logger.info("FAISS index loaded with %d vectors", len(document_vectors))

def preprocess_query(query):
    """Enhance pillar-related queries for better retrieval"""
    pillar_keywords = ['pillar', 'framework', 'principle', 'well-architected']
    
    if any(keyword in query.lower() for keyword in pillar_keywords):
        # Add context to improve retrieval for pillar queries
        enhanced_query = f"{query} AWS Well-Architected Framework six pillars principles"
        logger.info(f"Enhanced query: {enhanced_query}")
        return enhanced_query
    
    return query

def embed_text(text):
    logger.info(f"Embedding query: {text}")
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        body=json.dumps({"inputText": text}),
        contentType="application/json",
        accept="application/json"
    )
    response_body = json.loads(response["body"].read())
    return response_body["embedding"]

def lambda_handler(event, context):
    global index_loaded

    try:
        query = event.get("query")
        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing 'query' in payload"})
            }

        logger.info(f"Original query: {query}")

        if not index_loaded:
            load_faiss_from_s3()

        # Preprocess query for better retrieval
        enhanced_query = preprocess_query(query)
        
        # Increase k for pillar-related queries to get more comprehensive context
        pillar_keywords = ['pillar', 'framework', 'principle', 'well-architected', 'how many']
        k = 7 if any(keyword in query.lower() for keyword in pillar_keywords) else 3
        
        logger.info(f"Using k={k} for retrieval")

        query_vector = np.array([embed_text(enhanced_query)], dtype='float32')
        D, I = faiss_index.search(query_vector, k)

        results = []
        for i, (idx, distance) in enumerate(zip(I[0], D[0])):
            if idx != -1:
                text = document_texts[idx]
                results.append({"text": text, "similarity": float(1/(1+distance))})
                logger.info(f"Retrieved doc {i+1}: {text[:100]}... (similarity: {1/(1+distance):.3f})")

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x["similarity"], reverse=True)

        logger.info(f"Returning {len(results)} documents")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "documents": results,
                "debug_info": {
                    "original_query": query,
                    "enhanced_query": enhanced_query,
                    "k_used": k,
                    "total_retrieved": len(results)
                }
            })
        }

    except Exception as e:
        logger.exception("Error in retrieval function")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }