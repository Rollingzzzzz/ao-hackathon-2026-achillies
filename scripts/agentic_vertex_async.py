import os
import sys
import asyncio
import argparse
import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src", "1_data_loader"))

# Dynamically import agentic module
agentic_mod_path = os.path.join(project_root, "src", "1_data_loader", "agentic_vertex_async.py")
spec = importlib.util.spec_from_file_location("agentic_vertex_async", agentic_mod_path)
agentic_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agentic_mod)


async def main():
    parser = argparse.ArgumentParser(description="achillies X-Factor 2 Agentic Self-Healing Regex Finder Runner")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to the target raw log file for autonomous regex discovery & zero-loss normalization"
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=7,
        help="Maximum self-healing loop iterations (default: 7)"
    )
    parser.add_argument(
        "--max-regex-len",
        type=int,
        default=1000,
        help="Circuit Breaker Safeguard: Maximum allowed regex character length (default: 1000)"
    )
    parser.add_argument(
        "--max-sub-rules",
        type=int,
        default=25,
        help="Circuit Breaker Safeguard: Maximum allowed sub-rules in composite regex (default: 25)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional custom report .txt filepath (defaults to output_<input_basename>.txt)"
    )
    parser.add_argument(
        "--normalized-out", "-nout",
        type=str,
        default=None,
        help="Optional custom normalized single-line log .log filepath (defaults to normalized_<input_basename>.log)"
    )

    args = parser.parse_args()
    log_path = os.path.abspath(args.input)
    
    if not os.path.exists(log_path):
        print(f"❌ Target log file not found: {log_path}")
        return

    # Derive default file paths
    input_base = os.path.basename(log_path)
    input_name_no_ext = os.path.splitext(input_base)[0]
    out_dir = os.path.dirname(log_path)
    
    # 1. Execution Report TXT Path
    if args.output:
        out_txt_path = os.path.abspath(args.output)
    else:
        out_txt_path = os.path.join(out_dir, f"output_{input_name_no_ext}.txt")

    # 2. Normalized Single-Line Events Log Path
    if args.normalized_out:
        norm_log_path = os.path.abspath(args.normalized_out)
    else:
        norm_log_path = os.path.join(out_dir, f"normalized_{input_name_no_ext}.log")

    print("==========================================================================")
    print("⚡ X-FACTOR 2: AGENTIC VERTEX AI SELF-HEALING REGEX DISCOVERY TEST RUNNER")
    print("==========================================================================")
    print(f"• Target Log File        : {log_path}")
    print(f"• Max Iterations         : {args.iterations}")
    print(f"• Max Regex Length       : {args.max_regex_len} char")
    print(f"• Max Sub-Rules          : {args.max_sub_rules} rules")
    print(f"• Output TXT Report      : {out_txt_path}")
    print(f"• Normalized Events Log  : {norm_log_path}")
    print("==========================================================================")
    
    result = await agentic_mod.agentic_vertex_async_discovery(
        log_path,
        max_iterations=args.iterations,
        max_regex_length=args.max_regex_len,
        max_sub_rules=args.max_sub_rules
    )

    # 1. Save normalized single-line events to disk (.log file)
    normalized_events = result.get("normalized_events", [])
    if normalized_events:
        with open(norm_log_path, "w", encoding="utf-8") as f:
            for event in normalized_events:
                f.write(event + "\n")
        print(f"\n✅ Tekli satıra dönüştürülmüş ham loglar başarıyla yazıldı: {norm_log_path} ({len(normalized_events)} olay)")

    # 2. Generate Execution & Consumption Report
    report_lines = []
    report_lines.append("==========================================================================")
    report_lines.append("🏆 ACHILLIES AGENTIC SELF-HEALING REGEX FINDER EXECUTION REPORT")
    report_lines.append("==========================================================================")
    report_lines.append(f"• Input File          : {log_path}")
    report_lines.append(f"• Result Status       : {result['status']}")
    
    if "error_message" in result:
        report_lines.append(f"• Error Safeguard     : {result['error_message']}")
        
    report_lines.append(f"• Iterations Taken    : {result['iterations_taken']}")
    report_lines.append(f"• Verified Regex      : {result['verified_regex']}")
    report_lines.append(f"• Coverage Score      : %{result['coverage_score']}")
    report_lines.append(f"• Total Raw Lines     : {result['total_raw_lines']}")
    report_lines.append(f"• Events Produced     : {result['events_produced']}")
    report_lines.append(f"• Normalized Log File : {norm_log_path}")
    
    if "token_usage" in result:
        tu = result["token_usage"]
        report_lines.append("--------------------------------------------------------------------------")
        report_lines.append("🔥 TOKEN ACCOUNTING & COST REPORT:")
        report_lines.append(f"• Prompt Tokens       : {tu['prompt_tokens']} Token")
        report_lines.append(f"• Cached Tokens       : {tu['cached_tokens']} Token")
        report_lines.append(f"• Completion Tokens   : {tu['completion_tokens']} Token")
        report_lines.append(f"• Total Tokens Burned : {tu['total_tokens_burned']} Token")
        report_lines.append(f"• Estimated API Cost  : ${tu['estimated_cost_usd']:.6f} USD")
    report_lines.append("==========================================================================")

    report_text = "\n".join(report_lines)

    # Print report to stdout
    print("\n" + report_text)

    # Auto-save report TXT file
    with open(out_txt_path, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")
    
    print(f"\n✅ Yürütme ve tüketim raporu kaydedildi: {out_txt_path}")


if __name__ == "__main__":
    asyncio.run(main())
