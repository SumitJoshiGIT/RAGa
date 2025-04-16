## Introduction 

This is raga , a lib to facilitate rag setups .The motivation for this project lies in a hackathon I am participating in on campus Graphethon.
Its conditioned to work well with RaspberryPi based robots and any other app.

## Present State
Right now i have setup a api for the service and rag store though testing is still due.

### Embedding Methods

Well there are two methods possible for our application 

1. Offload Retrieval to a service 
   Pros: This allows us to run transformer based embedding models for rich embeddings
   Cons: Obv its not a local solution so latency 

2. Use simpler methods like Fast Text [Really SubOptimal but local]
   Pros: Can run locally and is fast  
   Cons: Accuracy is way worse so this has to be tested and tuned and results are skeptical  

So what are we doing?Same question 

For now i have made an api for Approach 1. 
and i plan to test Approach 2. as well but later 

## Choice of Vector Store 

Here as well we have a handful of choices:

 1. Postgres with pgvector extension
 2. Specialized vector stores:Pinecone ,Qdrant etc 

 I have defaulted to pgvector here right now for testing 
 Though i plan to integrate Pinecone instead for performance if needed 
 
| Dataset Size | pgvector (IVFFlat)               | Pinecone          |
|--------------|----------------------------------|-------------------|
| ~10K vectors | 5–50ms (CPU-bound)              | ~5–15ms           |
| ~100K+       | 50–300ms (depends on RAM, index tuning) | ~10–30ms          |
| ~1M+         | Often slow (unless well-tuned + RAM-heavy) | Scales fine        |

### Flow Optimization Proposals 

1. WebSockets 
 
 We can use web sockets for communication between the client and the service 
 Pros:
 1. Latency per request	on https:(~100–300ms avg)	websocket:(~10–50ms avg)
 Cons:
 1. Doesnt work on serverless setups like vercel 

2. Response Caching and Pre-Caching for gpt responses

 We can cache responses from gpt into the vector store then do similarity search to see if we have something that matches this already 
 Additionally can build a cache beforehand 
 
 Conditions:
 1. If we integrate the whole setup of generation to the service then we can do this efficiently 
 2. Again for accuracy transformers are required for embedding


### Next up 
1. Integration with Pi 
2. Scrapping data for RAG

