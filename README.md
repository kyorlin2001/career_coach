---
title: Career Coach
emoji: 🤖
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: "6.13.0"
python_version: "3.10"
app_file: app.py
pinned: false
---

# Career Coach

Career Coach is a Gradio-based AI assistant for job seekers, built as part of the IBM Generative AI Professional Certificate and later refactored for Hugging Face deployment.

The project includes tools for:

- career advice
- cover letters
- resume polishing
- general Q&A
- a unified demo interface for navigating the tools

## Overview

This repository shows both the learning project and the refactored portfolio version. It was originally created in a Watsonx-based course environment and later migrated to Hugging Face Inference to make it easier to deploy, maintain, and present in a portfolio setting.

The final structure keeps the individual demo scripts while also providing a single unified Gradio app for recruiters and reviewers to explore.

## Features

- **Career Advisor** — suggests ways to improve a resume for a target role
- **Cover Letter Generator** — drafts tailored cover letters
- **Resume Polisher** — improves resume wording, clarity, and ATS readability
- **General Chat** — a simple Q&A assistant for career-related questions
- **Unified Gradio App** — combines the tools into one interface

## Project Goals

- Demonstrate practical AI tools for job search support
- Show prompt engineering for different career-focused tasks
- Refactor a project from one model provider to another
- Keep the codebase clean, modular, and deployable
- Present a portfolio-ready Hugging Face Space

## Tech Stack

- Python 3.10
- Gradio
- Hugging Face Hub
- Hugging Face Inference API
- PyTorch
- Transformers

## How It Works

The app uses a shared Hugging Face inference helper so the model configuration lives in one place while each tool keeps its own prompt and behavior.

That design makes it easy to:

- reuse the same model backend
- keep prompts specialized by task
- maintain standalone demo scripts
- present everything through one unified app

## Repository Structure

- `app.py` — unified Gradio application
- `hf_client.py` — shared Hugging Face inference helper
- `career_advisor.py` — career advice tool
- `cover_letter.py` — cover letter generator
- `resume_polisher.py` — resume improvement tool
- `simple_llm.py` — basic Hugging Face inference demo
- `simple_llm_gradio.py` — simple Gradio chat demo
- `watson_ai_local.py` — earlier Watsonx-based reference work
- `requirements.txt` — project dependencies

## Getting Started

1. Create and activate a virtual environment
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Hugging Face token in the environment as `HF_TOKEN`
4. Run the unified app:
   ```bash
   python app.py
   ```

## Notes for Reviewers

This repository reflects a cleaned-up portfolio version of a class project.

The codebase was intentionally kept modular so it can show:

- the original learning demos
- the refactored Hugging Face implementation
- the final unified app for deployment and presentation

If you'd like to inspect the earlier implementation path, the git history preserves that progression.