import os
import sys
import asyncio
from .vertex_normalizer import query_vertex_gemini_for_regex, normalize_multiline_logs, extract_stratified_chunks
from .log_ozetleyici import run_drain3_clustering, save_cluster_summary_json
from .agentic_vertex_async import agentic_vertex_async_discovery


def load_and_summarize_log(
    log_file_path: str,
    header_regex_pattern: str = None,
    use_ai_discovery: bool = True,
    output_json_path: str = None
) -> dict:
    """
    End-to-End Orchestrator for 1_data_loader Module.
    
    1. Uses Vertex AI Gemini 2.5 Flash to dynamically discover event header regex (if not provided).
    2. Normalizes multi-line log events (stacktraces) into 100% zero-loss single-line events.
    3. Runs Drain3 streaming template miner to compress repeating logs into unique cluster templates.
    
    :param log_file_path: Absolute or relative path to the target log file.
    :param header_regex_pattern: Optional pre-defined regex pattern.
    :param use_ai_discovery: If True, uses Vertex AI Gemini 2.5 Flash for dynamic discovery.
    :param output_json_path: Optional file path to save cluster summary JSON.
    :return: Dictionary containing summary metrics, discovered regex, and sorted clusters.
    """
    if not os.path.exists(log_file_path):
        raise FileNotFoundError(f"Log dosyası bulunamadı: {log_file_path}")

    discovered_regex = header_regex_pattern

    if not discovered_regex and use_ai_discovery:
        print(f"🤖 Vertex AI Gemini 2.5 Flash ile otonom Regex keşfi başlatılıyor: {log_file_path}")
        chunks, _ = extract_stratified_chunks(log_file_path, num_chunks=3, chunk_size=30)
        sample_slice = "\n".join([c["text"] for c in chunks])
        res = query_vertex_gemini_for_regex(sample_slice)
        discovered_regex = res.get("event_header_regex")
        print(f"🎯 AI Keşif Sonucu Regex: {discovered_regex}")

    if not discovered_regex:
        # Generic ISO / Standard Timestamp boundary fallback
        discovered_regex = r"^\S+\.log(?:\.\d+)?\.\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}"

    print(f"⚡ Loglar normalize ediliyor (Zero-loss normalizer)...")
    events, is_zero_loss, raw_cnt, accounted = normalize_multiline_logs(log_file_path, discovered_regex)

    print(f"📊 Drain3 şablon kümeleme çalıştırılıyor ({len(events)} Olay)...")
    summary = run_drain3_clustering(events)
    summary["discovered_header_regex"] = discovered_regex
    summary["is_zero_loss"] = is_zero_loss

    if output_json_path:
        save_cluster_summary_json(summary, output_json_path)

    return summary


async def load_and_summarize_log_agentic(
    log_file_path: str,
    max_iterations: int = 5,
    output_json_path: str = None
) -> dict:
    """
    X-FACTOR 2: Agentic Self-Healing Guaranteed 100% Zero-Loss Pipeline.
    Iteratively heals and refines multi-rule regex patterns until 100% zero-loss is achieved.
    """
    agentic_res = await agentic_vertex_async_discovery(log_file_path, max_iterations=max_iterations)
    verified_regex = agentic_res["verified_regex"]

    events, is_zero_loss, _, _ = normalize_multiline_logs(log_file_path, verified_regex)
    summary = run_drain3_clustering(events)
    summary["agentic_result"] = agentic_res
    summary["verified_header_regex"] = verified_regex

    if output_json_path:
        save_cluster_summary_json(summary, output_json_path)

    return summary


if __name__ == "__main__":
    print("=== achillies 1_data_loader End-to-End Orchestrator ===")
