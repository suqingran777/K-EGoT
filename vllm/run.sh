#!/bin/bash

# 输出日志文件
output_file="vllm_output"

export CUDA_VISIBLE_DEVICES=2

# 使用nohup在后台运行vllm服务，将输出重定向到日志文件
nohup vllm serve /data1/guanyandong01/starlake/graduation/model/Qwen/Qwen3-8B \
    --served-model-name Qwen3-8B \
    --tensor-parallel-size 1 \
    --port 10062 > ${output_file} 2>&1 &

# 打印进程ID方便后续管理
echo "vllm服务已在后台运行，进程ID: $!"