import torch
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer

# 初始化 Flask 应用
app = Flask(__name__)

# 模型路径
model_name = "../../../model/Qwen/Qwen3-8B"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
model.eval()
print("模型加载完成")

# 定义API端点
@app.route('/generate', methods=['POST'])
def generate_text():

    if model is None or tokenizer is None:
        return jsonify({"error": "Model is not loaded yet. Please wait or check server logs."}), 503

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Invalid request. 'prompt' key is required."}), 400
    
    enable_thinking = data.get('enable_thinking', False)
    max_new_tokens = data.get('max_new_tokens', 512)
    temperature = data.get('temperature', 0.7)
    do_sample = data.get('do_sample', True)
    top_p = data.get('top_p', 0.95)
    top_k = data.get('top_k', 50)
    repetition_penalty = data.get('repetition_penalty', 1.0)

    user_prompt = data.get('prompt')
    messages = [{'role': 'user', 'content': user_prompt}]

    try:
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=enable_thinking
        )

        model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

        with torch.no_grad():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.eos_token_id,
                temperature=temperature,
                do_sample=do_sample,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
            )
        
        print(model_inputs.input_ids.shape)
        print(generated_ids.shape)

        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist() 

        try:
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")

        return jsonify({"thinking_content": thinking_content, "content": content})

    except Exception as e:
        print(f"Error during text generation: {e}")
        return jsonify({"error": "An error occurred during text generation."}), 500


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=10062)