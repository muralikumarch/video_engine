# Headless Technical Video Engine

A data-driven, fully automated Python video production engine designed to generate technical YouTube videos from JSON scripts. The engine synthesizes neural speech, compiles architectural diagrams via Graphviz, renders code walkthrough cards, and encodes hardware-optimized 1080p MP4 videos with zero manual timeline editing.

---

## 📋 Table of Contents
1. [Architecture & Workflow](#-architecture--workflow)
2. [Prerequisites & System Binaries](#-prerequisites--system-binaries)
3. [Project Directory Layout](#-project-directory-layout)
4. [Environment Setup in Antigravity IDE](#-environment-setup-in-antigravity-ide)
5. [Complete Source Code Implementation](#-complete-source-code-implementation)
   - [requirements.txt](#1-requirementstxt)
   - [renderers/__init__.py](#2-renderersinitpy)
   - [renderers/slide_renderer.py](#3-renderersslide_rendererpy)
   - [renderers/code_renderer.py](#4-rendererscode_rendererpy)
   - [renderers/diagram_renderer.py](#5-renderersdiagram_rendererpy)
   - [engine.py](#6-enginepy)
   - [episodes/enterprise_rag.json](#7-episodesenterprise_ragjson)
6. [Execution & Run Instructions](#-execution--run-instructions)
7. [Troubleshooting & Hardware Optimization](#-troubleshooting--hardware-optimization)
8. [Adding New Episodes](#-adding-new-episodes)

---

## 🏗 Architecture & Workflow

The pipeline decouples content authoring from video compilation. You define scenes, narration, and technical visuals inside a declarative JSON file; the engine handles rendering, speech synthesis, and video encoding automatically.