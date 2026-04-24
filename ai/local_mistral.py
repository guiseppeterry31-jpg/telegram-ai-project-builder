import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os

# Global cache for model and tokenizer to avoid reloading
_model = None
_tokenizer = None

def load_model():
    """Load a smaller, more accessible model for local use"""
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print("Loading local model (small, fast)...")
        
        # Use a smaller model that's easier to download
        model_name = "microsoft/phi-2"  # 2.7B parameters, good for local
        
        try:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            _tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            _model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            _tokenizer.pad_token = _tokenizer.eos_token
            print(f"✅ Model {model_name} loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise Exception(f"Local model loading failed: {e}. Please use OpenRouter mode instead.")
    return _tokenizer, _model

def run_local_mistral(prompt):
    """Run prompt through local model and return response"""
    try:
        tokenizer, model = load_model()
        # Format prompt for the model
        formatted_prompt = f"Instruct: {prompt}\nOutput:"
        inputs = tokenizer(formatted_prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the response after the prompt
        if "Output:" in response:
            return response.split("Output:")[-1].strip()
        return response
    except Exception as e:
        raise Exception(f"Local model generation failed: {e}")
