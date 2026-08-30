# 🧪 Vertex AI Gemini 2.5 Flash Examples & Benchmarks

This folder contains verified raw inputs, AI outputs, and benchmark results produced by Vertex AI Gemini 2.5 Flash for autonomous multiline log format discovery.

## 📂 Files Included

1. `sample_input_hadoop.log`: Raw 100-line mid-stacktrace log slice from Hadoop container logs.
2. `gemini_response_hadoop.json`: Exact JSON response produced by Gemini 2.5 Flash.

## 📊 Zero-Loss Normalization Results

| Benchmark Dataset | Total Raw Lines | Events Produced | Multiline Stacktraces | Zero-Loss Status |
| :--- | :--- | :--- | :--- | :--- |
| **OpenStack Normal 2** (38 MB) | 1,000 | 997 | 3 | **PASSED ZERO-LOSS** |
| **OpenStack Abnormal** (5.18 MB) | 1,000 | 1,000 | 0 | **PASSED ZERO-LOSS** |
| **Hadoop Java Exception Log** | 1,000 | 105 | 53 | **PASSED ZERO-LOSS** |
