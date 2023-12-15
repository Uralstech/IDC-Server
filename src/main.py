# IDC AI Server
# Copyright 2023 URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED
# 
# This product includes software developed at
# URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED (https://uralstech.in/)
# by Udayshankar Ravikumar.

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import intel_extension_for_pytorch as ipex
import torch

from typing import List, Dict
from pydantic import BaseModel
from fastapi import FastAPI
from uvicorn import run

from middleware import UMiddleware

from firebase_admin import initialize_app as initialize_firebase_app

# Set GOOGLE_APPLICATION_CREDENTIALS env variable to Google Auth credentials file.

class ChatCompletionsRequest(BaseModel):
    # In the format:
    #   [ { "role": "system" | "user" | "assistant", "content" : Query }, ... ]
    messages: List[Dict[str, str]]

class ChatCompletionResult(BaseModel):
    reply: str

app: FastAPI = FastAPI(title="IDC AI Server", version="1.0.0")
app.add_middleware(UMiddleware, firebase_app=initialize_firebase_app())

model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v0.6"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = ipex.optimize(model)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, torch_dtype=torch.bfloat16, device_map="auto")

@app.post("/api/chat", response_model=ChatCompletionResult)
async def ask(request: ChatCompletionsRequest):
    prompt = pipe.tokenizer.apply_chat_template(request.messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    full_reply: str = outputs[0]["generated_text"]
    index: int = full_reply.find("<|assistant|>")

    if index == -1:
        return full_reply
    
    return { "reply" : full_reply[index + 14:] }

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)