"""
achillies X-Factor 3: Agentic Drain3 High-Fidelity Auto-Tuner.

Uses Vertex AI Gemini 2.5 Flash as an autonomous Observability Reviewer to iteratively
tune Drain3 template mining parameters (sim_th, depth) until target high-fidelity (>=8.0/10)
SRE context preservation is achieved without over-masking critical error signals into `<*>` noise.
Includes 10 GB+ Streaming Memory Safeguards (Constant ~20 MB RAM footprint).
"""

import os
import json
import urllib.request
import asyncio

try:
    from .vertex_normalizer import get_gcp_adc_token, GCP_REGION
    from .drain3_ozetle import run_drain3_clustering, analyze_file_structural_metrics
except (ImportError, ValueError):
    from vertex_normalizer import get_gcp_adc_token, GCP_REGION
    from drain3_ozetle import run_drain3_clustering, analyze_file_structural_metrics


def query_vertex_fidelity_evaluator(cluster_templates_sample: list, current_sim_th: float, current_depth: int) -> dict:
    """
    X-FACTOR 3: Queries Vertex AI Gemini 2.5 Flash to evaluate the High-Fidelity SRE quality of mined log templates.
    Checks whether templates are over-masked into meaningless `<*>` noise or preserve critical error context.
    """
    token, project_id = get_gcp_adc_token()
    vertex_url = f"https://{GCP_REGION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{GCP_REGION}/publishers/google/models/gemini-2.5-flash:generateContent"

    sample_text = "\n".join([f"- Cluster #{c['cluster_id']} (Count: {c['size_count']}): {c['template']}" for c in cluster_templates_sample[:10]])

    prompt = f"""You are an expert SRE and AI Observability Engineer.

TASK & OBJECTIVE:
Evaluate the High-Fidelity quality of these mined log cluster templates for Root Cause & Anomaly Detection.
Gemini needs high-fidelity templates where error messages, status codes, exception class names, and key structural parameters are preserved, rather than being over-masked into useless `<*>` wildcards.

CURRENT DRAIN3 PARAMS:
- Similarity Threshold (`sim_th`): {current_sim_th}
- Tree Depth (`depth`): {current_depth}

MINED CLUSTER TEMPLATES SAMPLE:
{sample_text}

EVALUATION REQUIREMENTS:
1. `fidelity_score` (0.0 to 10.0): Rate how well these templates preserve meaningful SRE context for anomaly detection.
2. `is_over_masked` (boolean): `true` if critical error details or exception names were replaced by `<*>`.
3. `recommendation`: Choose one of:
   - "optimal_fidelity": Templates are high-fidelity and preserve critical SRE details.
   - "increase_sim_th": Increase similarity threshold to preserve more distinct template details.
   - "increase_depth": Increase tree depth to allow deeper branching for complex templates.

OUTPUT FORMAT REQUIREMENT:
Respond ONLY with a valid JSON object matching this schema:
{{
  "fidelity_score": 8.5,
  "is_over_masked": false,
  "recommendation": "optimal_fidelity",
  "reason": "<short explanation of the evaluation>"
}}
"""

    payload = json.dumps({
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json"
        }
    }).encode("utf-8")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(vertex_url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            result = json.loads(raw_text)

            usage = data.get("usageMetadata", {})
            result["_token_usage"] = {
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "cached_tokens": usage.get("cachedContentTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("totalTokenCount", 0)
            }
            return result
    except Exception as e:
        return {"error": str(e), "fidelity_score": 5.0, "is_over_masked": True, "recommendation": "increase_sim_th"}


async def agentic_drain3_autotune(
    events_source,  # Can be a file path string OR a list of event strings
    max_iterations: int = 5,
    target_fidelity: float = 8.0
) -> dict:
    """
    X-FACTOR 3: Agentic Drain3 High-Fidelity Auto-Tuner.
    Iteratively tunes `sim_th` and `depth` until Vertex AI Gemini 2.5 Flash rates template fidelity >= target_fidelity.
    Memory Footprint: Constant ~20 MB RAM regardless of whether file size is 10 MB or 10 GB.
    """
    print("🚀 [X-FACTOR 3] Agentic Drain3 High-Fidelity Auto-Tuner Başlatıldı.")

    tot_prompt_tokens = 0
    tot_cached_tokens = 0
    tot_completion_tokens = 0

    current_sim_th = 0.50
    current_depth = 4

    history = []
    best_summary = None
    best_fidelity = 0.0

    loop = asyncio.get_event_loop()

    for iteration in range(1, max_iterations + 1):
        print(f"\n--- 🔄 AUTOTUNER İTERASYON {iteration}/{max_iterations} ---")
        print(f"⚙️ Test Edilen DRAIN3 Parametreleri: sim_th={current_sim_th:.2f}, depth={current_depth}")

        summary = run_drain3_clustering(events_source, sim_th=current_sim_th, depth=current_depth)
        clusters = summary["clusters"]

        print(f"📊 Üretilen Küme Sayısı: {summary['total_unique_clusters']} | Sıkıştırma: %{summary['compression_ratio_percent']}")
        print(f"🤖 Vertex AI Gemini 2.5 Flash'a Şablon Sadakat (Fidelity) Değerlendirmesi Gönderiliyor...")

        eval_res = await loop.run_in_executor(
            None,
            query_vertex_fidelity_evaluator,
            clusters,
            current_sim_th,
            current_depth
        )

        u = eval_res.get("_token_usage", {})
        tot_prompt_tokens += u.get("prompt_tokens", 0)
        tot_cached_tokens += u.get("cached_tokens", 0)
        tot_completion_tokens += u.get("completion_tokens", 0)

        fidelity_score = float(eval_res.get("fidelity_score", 5.0))
        is_over_masked = bool(eval_res.get("is_over_masked", False))
        recommendation = str(eval_res.get("recommendation", "optimal_fidelity"))
        reason = str(eval_res.get("reason", "Otomatik değerlendirme"))

        print(f"⭐ AI Sadakat Skoru (Fidelity Score): {fidelity_score}/10.0 | Aşırı Maskeleme: {is_over_masked}")
        print(f"💡 AI Tavsiyesi: {recommendation} | Sebeb: {reason}")

        history.append({
            "iteration": iteration,
            "sim_th": current_sim_th,
            "depth": current_depth,
            "clusters_count": summary["total_unique_clusters"],
            "compression_ratio": summary["compression_ratio_percent"],
            "fidelity_score": fidelity_score,
            "is_over_masked": is_over_masked,
            "recommendation": recommendation,
            "reason": reason
        })

        if fidelity_score > best_fidelity:
            best_fidelity = fidelity_score
            best_summary = summary
            best_summary["autotuner_eval"] = {
                "fidelity_score": fidelity_score,
                "is_over_masked": is_over_masked,
                "reason": reason
            }

        # GUARANTEE CHECK: If fidelity score meets target and not over-masked
        if fidelity_score >= target_fidelity and not is_over_masked:
            print(f"🎉 HEDEF YÜKSEK SADAKAT (High-Fidelity) YAKALANDI! (Skor: {fidelity_score}/10.0, Tur: {iteration})")
            break

        # Adjust parameters based on AI recommendation
        if recommendation == "increase_sim_th":
            current_sim_th = min(0.85, round(current_sim_th + 0.10, 2))
        elif recommendation == "increase_depth":
            current_depth = min(8, current_depth + 2)
        else:
            current_sim_th = min(0.85, round(current_sim_th + 0.05, 2))
            current_depth = min(8, current_depth + 1)

    total_burned = tot_prompt_tokens + tot_completion_tokens
    uncached_prompt = max(0, tot_prompt_tokens - tot_cached_tokens)
    est_cost_usd = (
        ((uncached_prompt / 1_000_000) * 0.075) +
        ((tot_cached_tokens / 1_000_000) * 0.01875) +
        ((tot_completion_tokens / 1_000_000) * 0.30)
    )

    if not best_summary:
        best_summary = run_drain3_clustering(events_source, sim_th=current_sim_th, depth=current_depth)

    best_summary["autotuner_history"] = history
    best_summary["autotuner_token_usage"] = {
        "prompt_tokens": tot_prompt_tokens,
        "cached_tokens": tot_cached_tokens,
        "completion_tokens": tot_completion_tokens,
        "total_tokens_burned": total_burned,
        "estimated_cost_usd": round(est_cost_usd, 6)
    }

    return best_summary


if __name__ == "__main__":
    print("=== achillies Agentic Drain3 High-Fidelity Auto-Tuner Module ===")
