import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# Global cache for model and tokenizer to avoid reloading
_model = None
_tokenizer = None

def load_model():
    """Load Mistral 7B Instruct with 4-bit quantization (low memory, Colab compatible)"""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print("Loading local Mistral 7B model (4-bit quantized)...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
        _tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct")
        _model = AutoModelForCausalLM.from_pretrained(
            "mistralai/Mistral-7B-Instruct",
            quantization_config=bnb_config,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        _tokenizer.pad_token = _tokenizer.eos_token
    return _tokenizer, _model

def run_local_mistral(prompt):
    """Run prompt through local Mistral model and return response"""
    tokenizer, model = load_model()
    # Format prompt for Mistral Instruct architecture
    formatted_prompt = f"[INST] {prompt} [/INST]"
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=4096,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract only the response after the [/INST] tag
    return response.split("[/INST]")[-1].strip()
