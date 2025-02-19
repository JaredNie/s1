from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

# 请将 ${uid} 替换为实际生成的时间戳
model_path = "ckpts/s1-20250218_234238"

model = LLM(
    model_path,
    tensor_parallel_size=1,
)
tok = AutoTokenizer.from_pretrained(
    model_path
)

stop_token_ids = tok("<|im_end|>")["input_ids"]
sampling_params = SamplingParams(
    max_tokens=8192,
    min_tokens=0,
    stop_token_ids=stop_token_ids,
    skip_special_tokens=False,
    temperature=0.0,
)

# For the exact raspberry sample in the paper, change
# model to `qfq/1k_qr_bt_dm_po_steps` (an earlier version of s1)
# prompt to `How many r in raspberry?`
prompts = [
    "3.11和3.8相比，谁的数值更大？",
]
#prompts = [
#    "How many r in raspberry",
#]

for i, p in enumerate(prompts):
    prompt = "<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n" + p + "<|im_end|>\n<|im_start|>assistant\n"

    o = model.generate(
        prompt,
        sampling_params=sampling_params
    )

    print("No budget forcing:")
    print(prompt + o[0].outputs[0].text)
    print("-" * 80)

    with open(f"output_x.txt", "a") as f:
        f.write(prompt + o[0].outputs[0].text)
        f.write("\n" + "-" * 80 + "\n")

    stop_token_ids = tok("<|im_start|><|im_end|>")["input_ids"]
    sampling_params = SamplingParams(
        max_tokens=8192,
        min_tokens=0,
        stop_token_ids=stop_token_ids,
        skip_special_tokens=False,
        temperature=0.0,
    )
    prompt += "<|im_start|>think"
    o = model.generate(
        prompt,
        sampling_params=sampling_params
    )
    ignore_str = "Wait"

    # Num of times to skip stop token
    for i in range(1):
        prompt += o[0].outputs[0].text + ignore_str
        sampling_params = SamplingParams(
            max_tokens=8192,
            min_tokens=1,
            stop_token_ids=stop_token_ids,
            skip_special_tokens=False,
            temperature=0.0,
        )
        o = model.generate(
            prompt,
            sampling_params=sampling_params
        )

    ### Final answer ###
    prompt += o[0].outputs[0].text
    stop_token_ids = tok("<|im_end|>")["input_ids"]
    sampling_params = SamplingParams(
        max_tokens=8192,
        min_tokens=0,
        stop_token_ids=stop_token_ids,
        skip_special_tokens=False,
        temperature=0.0,
    )
    o = model.generate(
        prompt,
        sampling_params=sampling_params,
    )
    print("With budget forcing:")
    print(prompt + o[0].outputs[0].text)

    with open(f"output_x.txt", "a") as f:
        f.write(prompt + o[0].outputs[0].text)
        f.write("\n" + "-" * 80 + "\n")
