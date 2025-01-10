# Kindred AI

Kindred AI is a personalized family legacy chatbot that empowers grandparents to engage in meaningful conversations with an AI. Built with Cerebras for fast and efficient processing, it preserves family stories in a secure vector database and provides an intuitive interface for easy use.

---

## Features
- **Personalized Conversations**: Engage in rich, dynamic chats powered by AI with memory capabilities.
- **Fast Performance**: Powered by Cerebras for rapid inferencing and smooth interactions.
- **Secure Memory Storage**: Stores and retrieves conversations in a secure vector database for long-term preservation.
- **Scalable Design**: Leverages AWS for cloud storage and orchestration to ensure seamless operation.
- **User-Friendly Interface**: Built using Svelte for an intuitive and responsive user experience.

---

## Tech Stack
- **Frontend**: Svelte
- **Backend**: FastAPI
- **Database**: Vector storage with Pinecone (or equivalent)
- **Cloud Infrastructure**: AWS for storage and orchestration
- **AI Model**: Llama 2 with retrieval systems
- **Processing**: Cerebras for fast inferencing

---

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- AWS account for deployment
- Cerebras access for inferencing

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/lyeric2022/kindred-ai.git
   cd kindred-ai