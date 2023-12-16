# IDC AI Server
# Copyright 2023 URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED
#
# This product includes software developed at
# URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED (https://uralstech.in/)
# by Udayshankar Ravikumar.

from transformers import AutoModelForCausalLM, AutoTokenizer
import intel_extension_for_pytorch as ipex

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

model_name: str = "stabilityai/stablelm-zephyr-3b"
model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

qconfig = ipex.quantization.default_dynamic_qconfig
prepared_model = ipex.quantization.prepare(model, qconfig)

model = ipex.quantization.convert(prepared_model)
model = ipex.optimize(model)

@app.post("/api/chat", response_model=ChatCompletionResult)
async def ask(request: ChatCompletionsRequest):
    request.messages.append({"role":"system","content":"Always give short, concise replies."})

    prompt = tokenizer.apply_chat_template(request.messages, add_generation_prompt=True, return_tensors='pt')
    tokens = model.generate(
        prompt.to(model.device),
        max_new_tokens=256,
        temperature=0.3,
        do_sample=True
    )

    decoded = tokenizer.decode(tokens[0], skip_special_tokens=False)

    prev_index = -2
    while True:
        index = decoded.find("<|assistant|>\n")
        index = 0 if index == -1 else index + 14

        if index == 0 or index == prev_index:
            break
        prev_index = index

    end = decoded.find("<|endoftext|>", index)
    if end == -1:
        end = len(decoded)

    print(f"{index} || {end} || {decoded}")
    return { "reply" : decoded[index:end] }

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8080)