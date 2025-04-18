# Approach 

So we dont have capacity to run transformer based inference on gpus
so its better to stick to a provider.I have opted for huggingface 
Why?
1. Perfect for single event 
2. Rate limit is like 30-50 request per minute 

As for the vector db i have opted for pinecone for performance 
and store location metadata for context 

3. To put together the whole flow i am using langchain 
   simple and scalable as compared to the predecessors

# Latency 

## Embeddings 

### Image
For image rag latency is not a problem at all since this is a backgroud task 

400-800 ms is expected per warm request 

### Text
100-300ms on openai text-embedding-3-small 

## LLM

gpt 3.5 turbo small(~30 tokens) 300-500 ms 
gpt 3.5 turbo medium(~500 toks) 500-800 ms 

## Pinecone

Query 30-80 ms for top 3 matches 
Insertion 10-40 ms

on 768 dim vectors 

## TTS 

150-400 ms 

## Overall 

1. The latency for Image RAG is alright as per our application 

2. The latency on Text prompts will be   
