import os
import logging
from cerebras.cloud.sdk import Cerebras

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_cerebras_model(api_key, model_name="llama3.1-8b"):
    logger.info("Initializing Cerebras client")
    client = Cerebras(api_key=api_key)
    return client, model_name

def generate_answer_cerebras(client, model_name, question, relevant_texts):
    logger.info("Generating answer for question: %s", question)
    context_block = "\n".join(relevant_texts)
    prompt = f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer as if you were the person:"
    logger.info("Generated prompt: %s", prompt)
    
    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    # Access the response attributes correctly
    answer = chat_completion.choices[0].message.content
    logger.info("Generated response: %s", answer)
    return answer