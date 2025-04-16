## Introduction 

This is RAGa, a app to facilitate quick RAG setups. The motivation for this project lies in a hackathon I am participating in on campus, Graphethon.
It is designed to work well with Raspberry Pi-based robots and other applications.

## Present State
Currently, I have set up an API in FastAPI for the service and RAG store using SQLAlchemy and Neon (a cloud database provider), though testing is still pending.

### Embedding Methods

Two methods are possible for our application:

1. **Offload Retrieval to a Service**  
   - **Pros**: Allows us to run transformer-based embedding models for rich embeddings.  
   - **Cons**: Not a local solution, so it introduces latency.  

2. **Use Simpler Methods like FastText** (suboptimal but local)  
   - **Pros**: Can run locally and is fast.  
   - **Cons**: Accuracy is significantly worse, requiring testing, tuning, and skepticism about results.  

### Current Approach  

For now, I have implemented an API for Approach 1.  
I plan to test Approach 2 later.

## Choice of Vector Store 

We have a handful of choices for the vector store:

1. **Postgres with pgvector extension**  
2. **Specialized vector stores**: Pinecone, Qdrant, etc.  

Currently, I have defaulted to pgvector for testing.  
However, I plan to integrate Pinecone for better performance if needed.
 
| Dataset Size | pgvector (IVFFlat)               | Pinecone          |
|--------------|----------------------------------|-------------------|
| ~10K vectors | 5–50ms (CPU-bound)              | ~5–15ms           |
| ~100K+       | 50–300ms (depends on RAM, index tuning) | ~10–30ms          |
| ~1M+         | Often slow (unless well-tuned + RAM-heavy) | Scales fine        |

### Flow Optimization Proposals 

1. WebSockets 
 
We can use WebSockets for communication between the client and the service.  

- **Pros**:  
  1. Latency per request: HTTPS (~100–300ms avg), WebSocket (~10–50ms avg).  

- **Cons**:  
  1. Does not work on serverless setups like Vercel.  

2. Response Caching and Pre-Caching for gpt responses

 We can cache responses from gpt into the vector store then do similarity search to see if we have something that matches this already 
 Additionally can build a cache beforehand 
 
 Revisions:
 1. If we add the whole setup of generation and retrieval to the service itself then we can achieve more efficiency
 2. Again for accuracy transformers are required for embedding so for caching its more efficient to shove the generation to the service itself


### Next up 
1. Integration with Pi 
2. Scrapping data for RAG

