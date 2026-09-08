# Enterprise RAG Architecture: Secure, Multi-Tenant Knowledge Engine

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Spring Boot 3.3+](https://img.shields.io/badge/Spring%20Boot-3.3+-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Cloud Native](https://img.shields.io/badge/Cloud-AWS%20%7C%20Azure-orange.svg)](#cloud-implementations)

Reference architecture and production implementation accompanying the YouTube deep dive: **"Beyond Toy RAG: Designing an Enterprise-Grade Knowledge System on AWS / Azure"**.

This repository provides an enterprise blueprint that replaces naive 20-line vector demos with a resilient, zero-trust, decoupled retrieval pipeline.

---

## 🏛 Architecture Overview

```
[ INGESTION PLANE (Async / Event-Driven) ]
SharePoint / S3 / Confluence
       │
       ▼
 [Event Grid / SQS] ──► [Ingestion Worker (Spring Boot on AKS/EKS)]
                             │
                             ├──► 1. Document Parsing & Structure Extraction
                             ├──► 2. Semantic & Hierarchical Chunking
                             ├──► 3. Embeddings (Titan v2 / text-embedding-3-large)
                             └──► 4. Indexing: Vector + BM25 + ACL Metadata
                                        │
                                        ▼
                           [Managed Hybrid Vector Store]
                           (Azure AI Search / OpenSearch)
                                        ▲
                                        │
[ QUERY PLANE (Synchronous) ]           │
User Query ──► [API Gateway (APIM / APIGW)]
                     │
                     ▼
             [Orchestrator Service (Spring Boot 3)]
                     │
                     ├──► 1. JWT Security Inspection (Entra ID / Cognito Claims)
                     ├──► 2. Pre-Filtered Hybrid Retrieval (Vector + BM25 + ACL)
                     ├──► 3. Cross-Encoder Re-ranking (Cohere / BGE)
                     ├──► 4. Context Budget Packing & Token Optimization
                     ├──► 5. Guardrail Evaluation (Bedrock Guardrails / Content Safety)
                     └──► 6. LLM Streaming Generation (Claude 3.5 / GPT-4o)
```

---

## 🔑 Core Enterprise Features

* **Zero-Trust Access Control (ACL Propagation):** Identity claims are mapped directly from OAuth2/OIDC tokens into the vector query layer as a hard filter. Chunks unauthorized for the caller never enter orchestrator memory.
* **Two-Stage Hybrid Retrieval:** Combines sparse lexical keyword retrieval (BM25) and dense embeddings via Reciprocal Rank Fusion (RRF), followed by a Cross-Encoder re-ranker.
* **Fault-Tolerant Microservices:** Built with Spring Boot 3, Spring AI, and Resilience4j for circuit breaking, thread-pool isolation, and timeout budgeting.
* **Dual-Cloud Reference Implementations:** Adaptable to either AWS native (S3, SQS, OpenSearch Serverless, Bedrock) or Azure native (Blob, Event Grid, Azure AI Search, Azure OpenAI).

---

## 📁 Repository Structure

```
├── .github/workflows/          # CI/CD pipelines (TDD, checkstyle, container build)
├── docs/                       # Architectural Decision Records (ADRs) & Diagrams
│   ├── adr-001-hybrid-retrieval.md
│   └── adr-002-acl-metadata-filtering.md
├── ingestion-worker/           # Async ingestion pipeline (Event listener & Chunking)
│   ├── src/main/java/...
│   └── pom.xml
├── query-orchestrator/         # Low-latency synchronous API & Orchestration
│   ├── src/main/java/...
│   │   ├── config/             # Spring AI & Cloud Security config
│   │   ├── model/              # Domain & DTO records
│   │   ├── service/            # Hybrid search, re-ranking & LLM orchestrator
│   │   └── web/                # REST / SSE streaming endpoints
│   └── pom.xml
├── terraform/                  # Infrastructure as Code
│   ├── aws/                    # OpenSearch Serverless, Bedrock, SQS, ECS
│   └── azure/                  # Azure AI Search, Event Grid, AKS, Azure OpenAI
└── docker-compose.yml          # Local developer test harness (LocalStack/Qdrant)
```

---

## 🚀 Quickstart (Local Development)

### Prerequisites
* Java 21+ JDK
* Maven 3.9+
* Docker Desktop & Compose

### 1. Start Local Infrastructure
Spin up a local hybrid search vector store and mock identity provider:
```bash
docker-compose up -d
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and set your preferred model credentials:
```bash
# AWS Bedrock Configuration
SPRING_AI_BEDROCK_AWS_REGION=us-east-1
SPRING_AI_BEDROCK_AWS_ACCESS_KEY=your_key
SPRING_AI_BEDROCK_AWS_SECRET_KEY=your_secret

# Alternatively: Azure OpenAI
SPRING_AI_AZURE_OPENAI_API_KEY=your_azure_key
SPRING_AI_AZURE_OPENAI_ENDPOINT=[https://your-resource.openai.azure.com/](https://your-resource.openai.azure.com/)
```

### 3. Run the Query Orchestrator
```bash
cd query-orchestrator
mvn clean spring-boot:run
```

### 4. Execute a Sample Authenticated Query
```bash
curl -X POST http://localhost:8080/api/v1/rag/query \
  -H "Authorization: Bearer <MOCK_JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "userQuery": "What are our internal data retention limits for GDPR compliance?",
    "candidateLimit": 50,
    "finalContextLimit": 5
  }'
```

---

## 🧪 Testing & Verification

This project enforces strict Test-Driven Development (TDD):
```bash
# Run unit & integration tests
mvn test

# Run architecture constraint tests (ArchUnit)
mvn test -Dtest=ArchitectureRulesTest
```

---

## 📺 Accompanying Video Walkthrough

This codebase directly mirrors the architecture presented in our deep-dive video:
* **Video Link:** [Beyond Toy RAG: Designing an Enterprise Knowledge System](https://youtube.com)
* **Topics Covered:** Chunking tradeoffs, BM25 vs. Dense search, Reciprocal Rank Fusion formulas, and preventing authorization leakage.

---

## 📄 License
This architecture is licensed under the [Apache 2.0 License](LICENSE).