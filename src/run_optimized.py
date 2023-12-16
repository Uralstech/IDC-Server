# IDC AI Server
# Copyright 2023 URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED
#
# This product includes software developed at
# URAV ADVANCED LEARNING SYSTEMS PRIVATE LIMITED (https://uralstech.in/)
# by Udayshankar Ravikumar.

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import intel_extension_for_pytorch as ipex
import torch

model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v0.6"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

qconfig = ipex.quantization.default_dynamic_qconfig
prepared_model = ipex.quantization.prepare(model, qconfig)

model = ipex.quantization.convert(prepared_model)
model = ipex.optimize(model)

pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, torch_dtype=torch.int8, device_map="auto")

def ask(request: str):
    prompt = pipe.tokenizer.apply_chat_template([{"role":"user","content":request}], tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=64, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)

    full_reply: str = outputs[0]["generated_text"]
    index: int = full_reply.find("<|assistant|>")

    if index == -1:
        return full_reply
    
    return full_reply[index + 14:]