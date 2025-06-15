import os

import modal

# Get VLLM API key from environment
VLLM_API_KEY = os.getenv("VLLM_API_KEY")

vllm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "vllm==0.9.1",
        "huggingface_hub[hf_transfer]==0.32.0",
        "flashinfer-python==0.2.6.post1",
        extra_index_url="https://download.pytorch.org/whl/cu128",
    )
    .env(
        {
            "HF_HUB_ENABLE_HF_TRANSFER": "1",  # faster model transfers
            "NCCL_CUMEM_ENABLE": "1",
        }
    )
)


MODEL_NAME = "mistralai/Magistral-Small-2506"
MODEL_REVISION = "48c97929837c3189cb3cf74b1b5bc5824eef5fcc"  # avoid nasty surprises when repos update!

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)

vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)


vllm_image = vllm_image.env({"VLLM_USE_V1": "1"})


FAST_BOOT = True

app = modal.App("magistral-small-vllm")

N_GPU = 2
MINUTES = 60  # seconds
VLLM_PORT = 8000


@app.function(
    image=vllm_image,
    gpu=f"A100:{N_GPU}",
    scaledown_window=15 * MINUTES,  # how long should we stay up with no requests?
    timeout=10 * MINUTES,  # how long should we wait for container start?
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
    secrets=[modal.Secret.from_name("vllm-api")],
)
@modal.concurrent(  # how many requests can one replica handle? tune carefully!
    max_inputs=32
)
@modal.web_server(port=VLLM_PORT, startup_timeout=10 * MINUTES)
def serve():
    import subprocess

    cmd = [
        "vllm",
        "serve",
        MODEL_NAME,
        "--tokenizer_mode",
        "mistral",
        "--config_format",
        "mistral",
        "--load_format",
        "mistral",
        "--tool-call-parser",
        "mistral",
        "--enable-auto-tool-choice",
        "--tensor-parallel-size",
        "2",
        "--revision",
        MODEL_REVISION,
        "--served-model-name",
        MODEL_NAME,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
    ]

    # enforce-eager disables both Torch compilation and CUDA graph capture
    # default is no-enforce-eager. see the --compilation-config flag for tighter control
    cmd += ["--enforce-eager" if FAST_BOOT else "--no-enforce-eager"]

    print(cmd)

    subprocess.Popen(" ".join(cmd), shell=True)
