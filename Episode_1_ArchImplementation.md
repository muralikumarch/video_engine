### Video Identity & Packaging

* **Working Title:** *Beyond Toy RAG: Designing an Enterprise-Grade Knowledge Architecture (AWS & Azure)*
* **Target Audience:** Senior Software Engineers, Technical Leads, and Cloud Solutions Architects transitioning into GenAI systems.
* **Format:** Whiteboard / Diagram breakdown + Architectural walkthrough + Real-world production code snippets (Java/Spring Boot & Cloud Native).
* **Length:** 18–22 minutes.

---

### The Hook & Cold Open (0:00 – 1:45)

#### Visual Hook (0:00 – 0:35)

* **On Screen:** Split screen. On the left: a basic 20-line Python demo (`vector_store.as_retriever() -> llm.invoke()`). Label it: *"The Weekend Demo"*. On the right: a realistic enterprise incident report or latency spike alert showing P99 = 8.4s, hallucinated policy data, and leaked confidential compensation documents. Label it: *"Production Reality"*.
* **Spoken Script:**
> "Anyone can connect a vector database to an LLM in 20 lines of code. It looks like magic in a local notebook. But the moment you drop that setup into an enterprise environment, it shatters.
> You face P99 latency spikes over eight seconds. Your LLM happily leaks sensitive executive compensation documents because your vector store has zero ACL awareness. And the finance team is furious because vector similarity returned a draft document from 2022 instead of the audited filing from last week.
> Toy RAG is a demo. Production RAG is a distributed systems problem."



#### The Problem Statement & Credibility (0:35 – 1:15)

* **Spoken Script:**
> "In this video, we are not building another generic prototype. We are designing a multi-tenant, zero-trust knowledge system capable of scaling across thousands of users and millions of documents—using enterprise architectural patterns on AWS and Azure."



#### Value Promise & Roadmap (1:15 – 1:45)

* **On Screen:** 4-layer architecture preview graphic:
1. *Decoupled Ingestion Pipeline*
2. *Hybrid Retrieval & Cross-Encoder Re-ranking*
3. *Zero-Trust Security & ACL Propagation*
4. *Observability, Guardrails & LLM Eval Harness*



---

### End-to-End Architecture Blueprint

An enterprise RAG system is split into **two strictly decoupled planes**: an asynchronous batch/event-driven Ingestion Plane and a low-latency, synchronous Query Plane.

```
[ INGESTION PLANE (Async / Event-Driven) ]
SharePoint / S3 / Confluence
       │
       ▼
 [Event Grid / SQS Event] ──► [Worker Microservice (Spring Boot / AKS / ECS)]
                                   │
                                   ├──► 1. Document Parsing & Structure Extraction
                                   ├──► 2. Semantic / Parent-Child Chunking
                                   ├──► 3. Embeddings (Amazon Titan / Azure OpenAI)
                                   └──► 4. Indexing: Vector + Lexical (BM25) + Metadata (ACLs)
                                              │
                                              ▼
                                 [Managed Vector Store / Hybrid Search]
                                 (Azure AI Search / OpenSearch / Qdrant)
                                              ▲
                                              │
[ QUERY PLANE (Low-Latency / Synchronous) ]   │
User Query ──► [API Gateway (APIM / AWS APIGW)]
                     │
                     ▼
             [Orchestrator Service]
                     │
                     ├──► 1. Identity & Token Inspection (Entra ID / Cognito Claims)
                     ├──► 2. Query Rewriter / HyDE / Decomposition
                     ├──► 3. Hybrid Retrieval with ACL Metadata Filter (Security Pruning)
                     ├──► 4. Cross-Encoder Re-ranker (Cohere / BGE-Reranker)
                     ├──► 5. Context Compression & Token Packing
                     ├──► 6. Guardrail Boundary Check (Bedrock Guardrails / Azure Content Safety)
                     └──► 7. LLM Generation (Bedrock Claude / Azure OpenAI GPT)
                                   │
                                   ▼
                            Streaming Output with Exact Source Citations

```

---

### Step-by-Step Technical Breakdown

#### Act 1: The Asynchronous Ingestion Plane (1:45 – 6:30)

* **Key Architecture Rule:** Never embed on the fly or bind ingestion synchronously to API lifecycles.
* **Document Parsing Pitfalls:** Why simple text splitters fail on PDFs, multi-column layouts, and tables.
* **Chunking Patterns:**
* *Fixed-size chunking:* 512–1024 tokens with 50-token overlap as a baseline.
* *Parent-Child / Hierarchical Chunking:* Storing small 128-token chunks for dense embedding retrieval, but mapping them to parent paragraphs (1,000 tokens) for LLM context assembly.


* **Cloud Implementation:**
* **AWS Stack:** S3 ObjectCreated $\to$ SQS / EventBridge $\to$ Ingestion Worker on ECS Fargate / EKS $\to$ Amazon Titan Embeddings v2 $\to$ Amazon OpenSearch Serverless / Qdrant.
* **Azure Stack:** Azure Blob $\to$ Event Grid $\to$ AKS Ingestion Microservice $\to$ Azure OpenAI `text-embedding-3-large` $\to$ Azure AI Search.



#### Act 2: The Two-Stage Hybrid Retrieval Engine (6:30 – 11:30)

* **The Fatal Flaw of Pure Vector Search:** Vector embeddings calculate semantic similarity, not exact fact matching. Searching for `"Form 10-K Section 404"` or specific error codes will frequently fail in pure dense retrieval.
* **The Production Solution: Hybrid Search + RRF:**
* Run **Dense Retrieval** (Cosine/Dot Product on embeddings) in parallel with **Sparse Retrieval** (BM25 lexical keyword search).
* Combine rankings using **Reciprocal Rank Fusion (RRF)**:

$$RRF\_Score(d \in D) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$



*(where $k \approx 60$, and $r_m(d)$ is the document rank in model $m$)*


* **Cross-Encoder Re-ranking:**
* Dense/sparse search returns Top-50 coarse candidates.
* A Cross-Encoder (e.g., Cohere Re-rank, BGE-reranker) scores query-document pairs simultaneously, trimming candidates down to the Top-5 high-signal chunks.



#### Act 3: Enterprise Security & ACL Propagation (11:30 – 15:00)

* **The Security Blindspot:** Standard vector databases return all matches regardless of who is asking.
* **Implementing Zero-Trust Metadata Filtering:**
* Extract user identity, roles, and group memberships from OAuth2 / JWT claims (Azure Entra ID or AWS Cognito).
* Ingestion stage tags each vector document chunk with an `authorized_security_principals` array matching source system permissions (e.g., SharePoint ACLs).
* Query-stage retrieval injects a mandatory pre-filter into the vector query payload:
```json
{
  "filter": "security_groups/any(g: search.in(g, 'Engineering, Lead_Managers, Staff_All'))"
}

```




* **Result:** Non-permitted chunks are never retrieved or loaded into RAM, preventing unauthorized context exposure.

#### Act 4: Orchestration, Guardrails & Observability (15:00 – 19:30)

* **Backend Orchestrator:** Running a resilient Java / Spring Boot (or Go/Python) microservice with client-side connection pooling, circuit breakers (Resilience4j), and timeout budgets.
* **Guardrails at the Boundary:**
* Enforcing token filtering and hallucination prevention via **Amazon Bedrock Guardrails** or **Azure AI Content Safety**.


* **Observability & Continuous Eval:**
* Distributed tracing with OpenTelemetry across API Gateway $\to$ Orchestrator $\to$ Vector Store $\to$ LLM.
* Measuring the core RAG Triad: **Context Relevance**, **Groundedness / Faithfulness**, and **Answer Relevance** using automated synthetic eval sets (Ragas / TruLens).



---

### Summary & Call to Action (19:30 – End)

* **Recap Punchline:**
> "Building for production means treating AI not as a black-box novelty, but as a component within a classic, disciplined distributed architecture: asynchronous indexing, hybrid retrieval, strict authorization filters, and end-to-end tracing."


* **Viewer Next Step:**
> "I've published the architecture diagrams and a reference Spring Boot microservice repository implementing hybrid retrieval with Azure AI Search and Bedrock down in the description. In the next video, we'll implement the actual code: setting up multi-turn autonomous tool-calling in Spring AI."