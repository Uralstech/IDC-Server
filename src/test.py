# IDC AI Server
# Copyright 2023 URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED
# 
# This product includes software developed at
# URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED (https://uralstech.in/)
# by Udayshankar Ravikumar.

import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict
import intel_extension_for_pytorch as ipex

model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v0.6"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = ipex.optimize(model)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, torch_dtype=torch.bfloat16, device_map="auto")

def ask(request: List[Dict[str, str]]) -> str:
    prompt = pipe.tokenizer.apply_chat_template(request, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    full_reply: str = outputs[0]["generated_text"]
    index: int = full_reply.find("<|assistant|>")

    if index == -1:
        return full_reply
    return full_reply[index + 14:]

history: List[Dict[str, str]] = [
    {
        "role" : "system",
        "content" : input("System: ")
    }
]

while True:
    history.append(
        {
            "role" : "user",
            "content" : input("User: ")
        }
    )

    output = ask(history)
    history.append(
        {
            "role" : "assistant",
            "content" : output
        }
    )

    print(output)