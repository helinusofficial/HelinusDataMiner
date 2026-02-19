# 📘 Helinus Data Miner --- Project Overview

**Helinus Data Miner** is a scalable biomedical literature harvesting
engine designed to automatically collect, organize, and store
open-access full-text scientific articles in structured XML format from
major public biomedical repositories.

This project enables researchers, data scientists, and AI developers to
construct large-scale scientific corpora directly from trusted
biomedical databases for downstream machine learning and natural
language processing (NLP) tasks.

Helinus Data Miner programmatically retrieves full-text research
articles from:

-   Europe PMC
-   PubMed Central (PMC)

All downloaded articles are:

-   Open Access
-   Full-Text
-   Machine-Readable (XML)

making them ideal for automated data pipelines and AI model training
workflows.

------------------------------------------------------------------------

## 🎯 Purpose

Modern Artificial Intelligence systems---especially those used in:

-   Biomedical NLP
-   Scientific Question Answering
-   Clinical Language Models
-   Knowledge Graph Construction
-   Research Trend Analysis
-   Literature-Based Discovery
-   Domain-Specific LLM Training

require large-scale structured scientific text corpora.

Helinus Data Miner is designed to bridge the gap between publicly
available scientific knowledge and AI-ready datasets by automatically
constructing structured literature repositories from open biomedical
research.

------------------------------------------------------------------------

## 📥 Data Sources

Helinus Data Miner collects full-text research articles using two
complementary pipelines:

### 1️⃣ Europe PMC Retrieval Engine

The first pipeline directly queries the Europe PMC RESTful API to
retrieve:

-   Article metadata
-   Titles
-   Abstracts
-   Publication dates
-   Open-access full-text XML documents

Articles are filtered based on:

-   Publication date range
-   Open-access availability
-   Keyword presence in Title or Abstract fields

Downloaded full-text articles are automatically categorized into
topic-based directories using rule-based semantic classification derived
from the article's title and abstract.

------------------------------------------------------------------------

### 2️⃣ PubMed → PMC Conversion Pipeline

The second pipeline utilizes the NCBI E-utilities API to:

-   Search for relevant publications in PubMed
-   Filter results to include:
    -   Human-related studies
    -   Free full-text availability
    -   Publication date constraints
-   Convert PubMed IDs (PMIDs) to corresponding PMC IDs
-   Retrieve full-text XML documents from PubMed Central

This pipeline supports authenticated API access via NCBI API Key for
high-throughput retrieval.

------------------------------------------------------------------------

## ⚙️ Filtering Capabilities

Helinus Data Miner supports flexible data acquisition through:

-   Keyword-based query filtering
-   Publication date range filtering
-   Open-access-only filtering
-   Human-study filtering (MeSH-based)
-   Topic-aware automatic categorization
-   Monthly time-sliced harvesting
-   Resume support for interrupted downloads

This enables the creation of highly targeted scientific datasets for
specific AI or research applications.

------------------------------------------------------------------------

## 🗂 Output Structure

Downloaded articles are stored hierarchically:

    /BASE_OUTPUT_DIR
        └── Year/
            └── Month/
                └── Category/
                    └── PMCXXXXXXX.xml

Each XML file contains:

-   Full article body
-   Structured sections
-   Figures & tables metadata
-   References
-   Author information
-   Publication metadata

All content is stored in a machine-readable format suitable for
automated parsing.

------------------------------------------------------------------------

## 🤖 AI & Machine Learning Applications

The generated corpus can be directly used in:

-   Transformer-based language model pretraining
-   Biomedical Named Entity Recognition (BioNER)
-   Scientific Summarization
-   Retrieval-Augmented Generation (RAG)
-   Domain-Adaptive Pretraining (DAPT)
-   Knowledge Extraction
-   Topic Modeling
-   Semantic Search Systems
-   Citation Network Analysis
-   Medical Information Retrieval

Due to the structured XML format and open-access licensing, the
collected data is particularly suitable for:

-   Training biomedical LLMs
-   Building AI research assistants
-   Developing clinical decision-support systems
-   Fine-tuning domain-specific NLP models

------------------------------------------------------------------------

## 🔁 Fault Tolerance

Helinus Data Miner implements:

-   Download resume support
-   Cursor-based pagination
-   Status checkpointing
-   Retry logic for failed requests
-   Rate-limit handling

ensuring reliable long-term harvesting of large-scale scientific
datasets.

------------------------------------------------------------------------

## 📦 Dataset Construction

Using Helinus Data Miner, users can construct custom scientific corpora
such as:

**Helinus OpenBio Corpus (HOBC)**

which can be utilized for training or evaluating domain-specific AI
systems.
