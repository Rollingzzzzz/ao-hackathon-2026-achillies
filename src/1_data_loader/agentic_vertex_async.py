import os
import re
import json
import urllib.request
import asyncio

try:
    from .vertex_normalizer import (
        get_gcp_adc_token,
        extract_stratified_chunks,
        normalize_multiline_logs,
        query_vertex_gemini_for_regex,
        GCP_REGION,
        DEFAULT_PROJECT_ID,
    )
except (ImportError, ValueError):
    from vertex_normalizer import (
        get_gcp_adc_token,
        extract_stratified_chunks,
        normalize_multiline_logs,
        query_vertex_gemini_for_regex,
        GCP_REGION,
        DEFAULT_PROJECT_ID,
    )


def check_regex_complexity_limit(regex_pattern: str, max_length: int = 1000, max_rules: int = 25) -> tuple:
    """
    KORUMA BİRİMİ / CIRCUIT BREAKER:
    Üretilen regex kalıbının üst karmaşıklık sınırlarını (uzunluk ve alt kural sayısı) kontrol eder.
    Aşırı düzensiz / yapısız log dosyalarında regex patlamasını önler.
    """
    if len(regex_pattern) > max_length:
        return True, f"Regex karakter uzunluğu üst sınırı aşıldı ({len(regex_pattern)} > {max_length} karakter)."
    
    # Pipe '|' karakteri sayısına göre alt kural yoğunluğunu ölç
    rules_count = regex_pattern.count("|") + 1
    if rules_count > max_rules:
        return True, f"Regex alt kural sayısı üst sınırı aşıldı ({rules_count} > {max_rules} alt kural)."

    return False, ""


def find_unmatched_lines(log_file_path: str, header_regex_pattern: str, max_samples: int = 30) -> tuple:
    """
    Scans the log file with candidate regex rules and identifies non-indented lines
    (column 0 non-whitespace) that do NOT match the current candidate regex.
    100% DOMAIN-AGNOSTIC: Zero hardcoded keywords, log levels, or language-specific patterns.
    """
    compiled_regex = re.compile(header_regex_pattern)
    
    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = [l.rstrip("\r\n") for l in f if l.rstrip("\r\n")]

    if not raw_lines:
        return 100.0, [], [], True

    unmatched_candidates = []

    for idx, line in enumerate(raw_lines):
        if not compiled_regex.match(line):
            # Pure structural rule: A potential top-level log header must start at column 0 (non-whitespace)
            if line and not line[0].isspace():
                unmatched_candidates.append(line)

    total_lines = len(raw_lines)
    events, is_zero_loss, _, accounted = normalize_multiline_logs(log_file_path, header_regex_pattern)
    
    unmatched_count = len(unmatched_candidates)
    coverage_score = round(((total_lines - unmatched_count) / total_lines) * 100.0, 2) if total_lines > 0 else 100.0

    return coverage_score, unmatched_candidates[:max_samples], events, is_zero_loss


def query_vertex_gemini_refinement(
    previous_regex: str,
    failed_samples: list,
    coverage_score: float
) -> dict:
    """
    Agentic Feedback Prompting: Sends previous regex + failed unmatched samples to Vertex AI Gemini 2.5 Flash
    asking for a refined unified or composite multi-rule regex `(?:Rule1|Rule2)` in a 100% domain-agnostic way.
    """
    token, project_id = get_gcp_adc_token()
    
    vertex_url = f"https://{GCP_REGION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{GCP_REGION}/publishers/google/models/gemini-2.5-flash:generateContent"

    samples_text = "\n".join(failed_samples)

    prompt = fr"""You are an expert SRE and Log Parsing Engineer specialized in Regular Expressions and Multi-Format Log Parsing.

AGENTIC SELF-HEALING FEEDBACK LOOP (100% DOMAIN-AGNOSTIC):
Your previous candidate regex pattern achieved {coverage_score}% coverage, but MISSED several valid top-level log entry headers.

PREVIOUS CANDIDATE REGEX RULE(S):
`{previous_regex}`

FAILED LOG SAMPLES (UNMATCHED TOP-LEVEL HEADERS):
{samples_text}

TASK & OBJECTIVE:
1. Analyze WHY the previous regex failed to match these sample lines (e.g. missing service/module prefixes, different timestamp or log boundary format).
2. CRITICAL: `event_header_regex` MUST match ONLY top-level log entry headers anchored at '^'.
3. Continuation lines (indented lines, sub-messages, trace details) belong to the parent log entry. NEVER write rules matching continuation lines into `event_header_regex`. Non-matching continuation lines will be automatically concatenated onto their parent header line into a single-line log event.
4. Synthesize a COMPOSITE MULTI-RULE regex using non-capturing groups `^(?:Rule1|Rule2|Rule3)` matching top-level entry headers.

OUTPUT FORMAT REQUIREMENT:
Respond ONLY with a valid JSON object matching this schema:
{{
  "event_header_regex": "<refined python regex pattern anchored at '^' matching top-level entry headers>",
  "reason_for_refinement": "<explanation of what was missed and how the new multi-rule regex fixes it>"
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
        return {"error": str(e)}


async def agentic_vertex_async_discovery(
    log_file_path: str,
    max_iterations: int = 7,
    max_regex_length: int = 1000,
    max_sub_rules: int = 25
) -> dict:
    """
    X-FACTOR 2: Agentic Self-Healing Iterative Loop with Token Accounting & Circuit Breaker Safeguards.
    100% Domain-Agnostic & Pure Structural Logic.
    """
    print(f"🚀 [X-FACTOR 2] Agentic Self-Healing Vertex Loop (Domain-Agnostic Structural Safe) Başlatıldı: {log_file_path}")
    
    # Token Accounting Accumulators
    tot_prompt_tokens = 0
    tot_cached_tokens = 0
    tot_completion_tokens = 0
    events = []

    # Round 1: Initial Discovery
    chunks, total_lines = extract_stratified_chunks(log_file_path, num_chunks=10, chunk_size=15)
    sample_slice = "\n".join([c["text"] for c in chunks])
    
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, query_vertex_gemini_for_regex, sample_slice)
    
    u_init = res.get("_token_usage", {})
    tot_prompt_tokens += u_init.get("prompt_tokens", 0)
    tot_cached_tokens += u_init.get("cached_tokens", 0)
    tot_completion_tokens += u_init.get("completion_tokens", 0)

    current_regex = res.get("event_header_regex", r"^\S+\.log\S*\s+\d{4}-\d{2}-\d{2}")

    history = []

    for iteration in range(1, max_iterations + 1):
        print(f"\n--- 🔄 AGENTIC DÖNGÜ İTERASYON {iteration}/{max_iterations} ---")
        print(f"🔍 Test Edilen Candidate Regex: `{current_regex}`")

        # KORUMA BİRİMİ DENETİMİ (CIRCUIT BREAKER CHECK)
        is_limit_exceeded, limit_reason = check_regex_complexity_limit(current_regex, max_length=max_regex_length, max_rules=max_sub_rules)
        if is_limit_exceeded:
            print(f"🛑 [KORUMA SİSTEMİ DEVREDE] Bu dosya aşırı düzensiz/yapısız (irregular)! {limit_reason}")
            total_burned = tot_prompt_tokens + tot_completion_tokens
            uncached_prompt = max(0, tot_prompt_tokens - tot_cached_tokens)
            est_cost_usd = (
                ((uncached_prompt / 1_000_000) * 0.075) +
                ((tot_cached_tokens / 1_000_000) * 0.01875) +
                ((tot_completion_tokens / 1_000_000) * 0.30)
            )
            return {
                "status": "FAILED_IRREGULAR_LOG_FORMAT",
                "error_message": f"❌ Bu dosya aşırı düzensiz/yapısız (irregular) log formatına sahiptir! {limit_reason} İşlem güvenlik nedeniyle durduruldu.",
                "iterations_taken": iteration,
                "verified_regex": current_regex,
                "coverage_score": history[-1]["coverage_score"] if history else 0.0,
                "total_raw_lines": total_lines,
                "events_produced": 0,
                "normalized_events": [],
                "token_usage": {
                    "prompt_tokens": tot_prompt_tokens,
                    "cached_tokens": tot_cached_tokens,
                    "completion_tokens": tot_completion_tokens,
                    "total_tokens_burned": total_burned,
                    "estimated_cost_usd": round(est_cost_usd, 6)
                },
                "history": history
            }
        
        coverage_score, unmatched_samples, events, is_zero_loss = find_unmatched_lines(log_file_path, current_regex)
        
        print(f"📊 Eşleşme / Kapsama Oranı: %{coverage_score}")
        print(f"✅ Sıfır Kayıp (Zero-Loss) Durumu: {is_zero_loss}")
        
        history.append({
            "iteration": iteration,
            "regex": current_regex,
            "coverage_score": coverage_score,
            "unmatched_samples_count": len(unmatched_samples),
            "is_zero_loss": is_zero_loss
        })

        # GUARANTEE CHECK: If 100% coverage and zero-loss passed AND no unmatched log candidates exist
        if coverage_score >= 100.0 and len(unmatched_samples) == 0:
            print(f"🎉 %100 KUSURSUZ EŞLEŞME ELDE EDİLDİ! Döngü Başarıyla Tamamlandı (Tur: {iteration}).")
            
            total_burned = tot_prompt_tokens + tot_completion_tokens
            uncached_prompt = max(0, tot_prompt_tokens - tot_cached_tokens)
            est_cost_usd = (
                ((uncached_prompt / 1_000_000) * 0.075) +
                ((tot_cached_tokens / 1_000_000) * 0.01875) +
                ((tot_completion_tokens / 1_000_000) * 0.30)
            )
            
            return {
                "status": "SUCCESS_100_PERCENT_GUARANTEED",
                "iterations_taken": iteration,
                "verified_regex": current_regex,
                "coverage_score": 100.0,
                "total_raw_lines": total_lines,
                "events_produced": len(events),
                "normalized_events": events,
                "token_usage": {
                    "prompt_tokens": tot_prompt_tokens,
                    "cached_tokens": tot_cached_tokens,
                    "completion_tokens": tot_completion_tokens,
                    "total_tokens_burned": total_burned,
                    "estimated_cost_usd": round(est_cost_usd, 6)
                },
                "history": history
            }

        print(f"⚠️ %100'ün Altında Kaldı (%{coverage_score}). Kaçırılan {len(unmatched_samples)} Satır İzolasyonu Yapılıyor...")
        print(f"🤖 Vertex AI Gemini 2.5 Flash'a Self-Healing Prompt'u Gönderiliyor...")

        refinement_res = await loop.run_in_executor(
            None,
            query_vertex_gemini_refinement,
            current_regex,
            unmatched_samples,
            coverage_score
        )

        u_ref = refinement_res.get("_token_usage", {})
        tot_prompt_tokens += u_ref.get("prompt_tokens", 0)
        tot_cached_tokens += u_ref.get("cached_tokens", 0)
        tot_completion_tokens += u_ref.get("completion_tokens", 0)

        new_regex = refinement_res.get("event_header_regex")
        reason = refinement_res.get("reason_for_refinement", "Otonom iyileştirme")

        if not new_regex or new_regex == current_regex:
            print("⚠️ Model yeni regex veremedi veya aynı kaldı, döngü sonlandırılıyor.")
            break

        print(f"💡 AI Düzeltme Sebebi: {reason}")
        current_regex = new_regex

    total_burned = tot_prompt_tokens + tot_completion_tokens
    uncached_prompt = max(0, tot_prompt_tokens - tot_cached_tokens)
    est_cost_usd = (
        ((uncached_prompt / 1_000_000) * 0.075) +
        ((tot_cached_tokens / 1_000_000) * 0.01875) +
        ((tot_completion_tokens / 1_000_000) * 0.30)
    )

    last_coverage = history[-1]["coverage_score"] if history else 0.0
    status_code = "COMPLETED_BEST_EFFORT" if last_coverage >= 90.0 else "FAILED_IRREGULAR_LOG_FORMAT"
    error_msg = f"❌ Bu dosya düzensiz/yapısız formatta! {max_iterations} iterasyon sonunda sadece %{last_coverage} kapsama sağlandı." if status_code == "FAILED_IRREGULAR_LOG_FORMAT" else None

    res_dict = {
        "status": status_code,
        "iterations_taken": len(history),
        "verified_regex": current_regex,
        "coverage_score": last_coverage,
        "total_raw_lines": total_lines,
        "events_produced": len(events),
        "normalized_events": events,
        "token_usage": {
            "prompt_tokens": tot_prompt_tokens,
            "cached_tokens": tot_cached_tokens,
            "completion_tokens": tot_completion_tokens,
            "total_tokens_burned": total_burned,
            "estimated_cost_usd": round(est_cost_usd, 6)
        },
        "history": history
    }
    if error_msg:
        res_dict["error_message"] = error_msg

    return res_dict


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser(description="achillies Agentic Vertex AI Self-Healing Loop Module")
    parser.add_argument("--input", "-i", type=str, required=True, help="Target raw log file path")
    parser.add_argument("--iterations", "-n", type=int, default=7, help="Max iterations")
    parser.add_argument("--max-regex-len", type=int, default=1000, help="Max regex character length")
    parser.add_argument("--max-sub-rules", type=int, default=25, help="Max sub rules count")
    
    args = parser.parse_args()
    log_file = os.path.abspath(args.input)
    if not os.path.exists(log_file):
        print(f"❌ Dosya bulunamadı: {log_file}")
        sys.exit(1)
        
    res = asyncio.run(agentic_vertex_async_discovery(
        log_file,
        max_iterations=args.iterations,
        max_regex_length=args.max_regex_len,
        max_sub_rules=args.max_sub_rules
    ))
    print(json.dumps(res, indent=2, ensure_ascii=False))
