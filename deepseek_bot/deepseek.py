import os
from deepseek_api import DeepseekAPI
from dotenv import load_dotenv

load_dotenv()
    

def deepseek(model: str) -> DeepseekAPI:
    return DeepseekAPI(email=os.getenv("DEEPSEEK_EMAIL"), password=os.getenv("DEEPSEEK_PASSWORD"), model_class=model, save_login=True)


def generate_response(deepseek, prompt: str):
    pending_response = ""
    # yield streaming response
    for message in deepseek.chat(prompt):
        pending_response += message["choices"][0]["delta"]["content"]
        if pending_response:
            yield pending_response
            pending_response = ""
    if pending_response:
        yield pending_response