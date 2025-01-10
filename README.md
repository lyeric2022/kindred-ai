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
- **Processing**: Cerebras for accelerated inferencing
- **Voice Synthesis**: F5-TTS for natural and expressive voice synthesis

---

## Installation

### Prerequisites
- Python
- Node.js
- Pinecone account for ingestion and RAG
- Cerebras access for inferencing
- Ideally a decent device with CUDA
- 

### Steps
1. **Clone the Repository**
   ```bash
   git clone https://github.com/lyeric2022/kindred-ai.git
   cd kindred-ai

2. **Installation**
   ```bash
    # Or run this instead: 
    source bash.sh

    # Create a virtual environment named 'venv'
    python3 -m venv venv

    # Activate the virtual environment
    source venv/bin/activate

    # Upgrade setuptools and wheel
    pip install --upgrade setuptools wheel

    # Download packages
    pip install -r requirements.txt

3. Initialize Environmental Variables
    ```bash
    # Create .env file to store environmental variables
    touch .env

    # Insert API keys    
    CEREBRAS_API_KEY = ""
    PINECONE_API_KEY = ""

4. Navigate to the svelte-app directory
   ```bash
    cd ../svelte-app

    # Install frontend dependencies
    npm install

    # Run the frontend server
    npm run dev

5. Navigate to the backend directory
   ```bash
    cd ../backend

    # Run the backend server
    python main.py

    # Run the backend server
    uvicorn app:app --reload

6. Access the App
    - open your browser and navigate to http://localhost:8080

---

## Usage
1. Start the backend and frontend as described in the installation steps.
2. Interact with the app by inputting stories and asking questions.
3. Upload voice audio to use voice synthesis.

---

## License
This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License. 
To view a copy of this license, visit https://creativecommons.org/licenses/by-nc/4.0/.

You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. 
- NonCommercial — You may not use the material for commercial purposes.

No additional restrictions — You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
