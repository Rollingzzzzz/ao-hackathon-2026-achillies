import os
import sys
import json
import asyncio
import argparse
import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src", "1_data_loader"))

# Dynamically import module
mod_path = os.path.join(project_root, "src", "1_data_loader", "agentic_drain3_autotuner.py")
spec = importlib.util.spec_from_file_location("agentic_drain3_autotuner", mod_path)
if spec and spec.loader:
    autotuner_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(autotuner_mod)


async def main():
    parser = argparse.ArgumentParser(description="achillies X-Factor 3 Agentic Drain3 High-Fidelity Auto-Tuner Runner")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to input normalized log file (one event per line)"
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=5,
        help="Maximum autotuner loop iterations (default: 5)"
    )
    parser.add_argument(
        "--target-fidelity",
        type=float,
        default=8.0,
        help="Target AI template fidelity score from 0.0 to 10.0 (default: 8.0)"
    )
    parser.add_argument(
        "--templates-out", "-tout",
        type=str,
        default=None,
        help="Optional custom filepath for ALL mined unique log templates (defaults to templates_<input_base>.txt)"
    )
    parser.add_argument(
        "--json-out", "-j",
        type=str,
        default=None,
        help="Optional custom output JSON summary filepath"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional custom output TXT execution report filepath"
    )

    args = parser.parse_args()
    log_path = os.path.abspath(args.input)

    if not os.path.exists(log_path):
        print(f"❌ Target log file not found: {log_path}")
        sys.exit(1)

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    # Derive default output paths if omitted
    input_base = os.path.basename(log_path)
    input_name_no_ext = os.path.splitext(input_base)[0]
    out_dir = os.path.dirname(log_path)

    templates_path = os.path.abspath(args.templates_out) if args.templates_out else os.path.join(out_dir, f"templates_{input_name_no_ext}.txt")
    json_path = os.path.abspath(args.json_out) if args.json_out else os.path.join(out_dir, f"summary_autotuner_{input_name_no_ext}.json")
    txt_path = os.path.abspath(args.output) if args.output else os.path.join(out_dir, f"output_autotuner_{input_name_no_ext}.txt")

    print("==========================================================================")
    print("⚡ X-FACTOR 3: AGENTIC DRAIN3 HIGH-FIDELITY AUTO-TUNER RUNNER")
    print("==========================================================================")
    print(f"• Target Log File      : {log_path}")
    print(f"• Max Iterations       : {args.iterations}")
    print(f"• Target Fidelity      : {args.target_fidelity}/10.0")
    print(f"• All Templates File   : {templates_path}")
    print(f"• Output JSON Summary  : {json_path}")
    print(f"• Output TXT Report    : {txt_path}")
    print("==========================================================================")

    result_summary = await autotuner_mod.agentic_drain3_autotune(
        raw_lines,
        max_iterations=args.iterations,
        target_fidelity=args.target_fidelity
    )

    stats = result_summary.get("file_structural_stats", {})
    cfg = result_summary.get("drain3_config", {})
    eval_info = result_summary.get("autotuner_eval", {})
    all_clusters = result_summary.get("clusters", [])

    # 1. Save ALL 100% mined unique templates to templates_<input_base>.txt
    template_lines = []
    template_lines.append("==========================================================================")
    template_lines.append("🏆 ACHILLIES AGENTIC DRAIN3 HIGH-FIDELITY ALL MINED LOG TEMPLATES")
    template_lines.append("==========================================================================")
    template_lines.append(f"• Input File           : {log_path}")
    template_lines.append(f"• Total Raw Events     : {result_summary.get('total_events_processed', 0)}")
    template_lines.append(f"• Total Unique Clusters: {len(all_clusters)}")
    template_lines.append(f"• Optimal Sim Threshold: {cfg.get('sim_th')}")
    template_lines.append(f"• Optimal Tree Depth   : {cfg.get('depth')}")
    template_lines.append(f"• AI Fidelity Score    : {eval_info.get('fidelity_score', 0.0)}/10.0")
    template_lines.append("==========================================================================")
    template_lines.append("ALL MINED LOG CLUSTER TEMPLATES (SORTED BY FREQUENCY):")
    template_lines.append("--------------------------------------------------------------------------")

    total_ev = max(result_summary.get("total_events_processed", 1), 1)
    for idx, c in enumerate(all_clusters, 1):
        pct = (c["size_count"] / total_ev) * 100.0
        template_lines.append(f"[{idx:04d}] Cluster #{c['cluster_id']:<4} | Count: {c['size_count']:<6} (%{pct:>5.2f}) | Template: {c['template']}")

    template_lines.append("==========================================================================")
    
    with open(templates_path, "w", encoding="utf-8") as f:
        f.write("\n".join(template_lines) + "\n")
    print(f"\n✅ Bütün (%100) şablonlar başarıyla kaydedildi: {templates_path} ({len(all_clusters)} şablon)")

    # 2. Save JSON summary
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_summary, f, ensure_ascii=False, indent=2)

    # 3. Generate Execution Report
    report_lines = []
    report_lines.append("==========================================================================")
    report_lines.append("🏆 ACHILLIES AGENTIC DRAIN3 HIGH-FIDELITY AUTO-TUNER REPORT")
    report_lines.append("==========================================================================")
    report_lines.append(f"• Input File          : {log_path}")
    report_lines.append(f"• Total Raw Lines     : {stats.get('total_lines', 0)}")
    report_lines.append(f"• Max Line Length     : {stats.get('max_line_length', 0)} char")
    report_lines.append(f"• Min Line Length     : {stats.get('min_line_length', 0)} char")
    report_lines.append(f"• Avg Line Length     : {stats.get('avg_line_length', 0.0)} char")
    report_lines.append("--------------------------------------------------------------------------")
    report_lines.append(f"• Processed Events    : {result_summary.get('total_events_processed', 0)}")
    report_lines.append(f"• Unique Clusters     : {result_summary.get('total_unique_clusters', 0)}")
    report_lines.append(f"• Compression Ratio   : %{result_summary.get('compression_ratio_percent', 0.0)}")
    report_lines.append(f"• Optimal Sim Threshold: {cfg.get('sim_th')}")
    report_lines.append(f"• Optimal Tree Depth  : {cfg.get('depth')}")
    report_lines.append(f"• AI Fidelity Score   : {eval_info.get('fidelity_score', 0.0)}/10.0")
    report_lines.append(f"• Over-Masked Status  : {eval_info.get('is_over_masked', False)}")
    report_lines.append(f"• All Templates File  : {templates_path}")
    
    if "autotuner_token_usage" in result_summary:
        tu = result_summary["autotuner_token_usage"]
        report_lines.append("--------------------------------------------------------------------------")
        report_lines.append("🔥 TOKEN ACCOUNTING & COST REPORT:")
        report_lines.append(f"• Prompt Tokens       : {tu['prompt_tokens']} Token")
        report_lines.append(f"• Cached Tokens       : {tu['cached_tokens']} Token")
        report_lines.append(f"• Completion Tokens   : {tu['completion_tokens']} Token")
        report_lines.append(f"• Total Tokens Burned : {tu['total_tokens_burned']} Token")
        report_lines.append(f"• Estimated API Cost  : ${tu['estimated_cost_usd']:.6f} USD")

    report_lines.append("==========================================================================")
    report_lines.append(f"TOP {min(10, len(all_clusters))} HIGH-FIDELITY LOG TEMPLATES:")
    report_lines.append("--------------------------------------------------------------------------")

    for idx, c in enumerate(all_clusters[:10], 1):
        pct = (c["size_count"] / total_ev) * 100.0
        report_lines.append(f"[{idx:02d}] Cluster #{c['cluster_id']:<3} | Count: {c['size_count']:<6} (%{pct:>5.2f}) | Template: {c['template']}")

    report_lines.append("==========================================================================")
    report_text = "\n".join(report_lines)

    print("\n" + report_text)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")

    print(f"\n✅ Yürütme raporu kaydedildi: {txt_path}")


if __name__ == "__main__":
    asyncio.run(main())
