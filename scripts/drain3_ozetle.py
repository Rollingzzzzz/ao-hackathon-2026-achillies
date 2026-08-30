import os
import sys
import argparse
import importlib.util

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src", "1_data_loader"))

# Dynamically import module
mod_path = os.path.join(project_root, "src", "1_data_loader", "drain3_ozetle.py")
spec = importlib.util.spec_from_file_location("drain3_ozetle", mod_path)
if spec and spec.loader:
    drain3_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(drain3_mod)


def main():
    parser = argparse.ArgumentParser(description="achillies Generic Drain3 Log Template Miner & Summarizer Runner")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Path to input normalized log file (one event per line)"
    )
    parser.add_argument(
        "--sim-th",
        type=float,
        default=0.5,
        help="Drain3 similarity threshold (default: 0.5)"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=4,
        help="Drain3 parse tree depth (default: 4)"
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=10,
        help="Print top N most frequent clusters to stdout (default: 10)"
    )
    parser.add_argument(
        "--json-out", "-j",
        type=str,
        default=None,
        help="Optional output JSON summary path (defaults to summary_drain3_<input_base>.json)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional output TXT report path (defaults to output_drain3_<input_base>.txt)"
    )

    args = parser.parse_args()
    log_path = os.path.abspath(args.input)

    if not os.path.exists(log_path):
        print(f"❌ Target log file not found: {log_path}")
        sys.exit(1)

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    summary = drain3_mod.run_drain3_clustering(raw_lines, sim_th=args.sim_th, depth=args.depth)
    stats = summary["file_structural_stats"]

    # Derive default output paths if omitted
    input_base = os.path.basename(log_path)
    input_name_no_ext = os.path.splitext(input_base)[0]
    out_dir = os.path.dirname(log_path)

    json_path = os.path.abspath(args.json_out) if args.json_out else os.path.join(out_dir, f"summary_drain3_{input_name_no_ext}.json")
    txt_path = os.path.abspath(args.output) if args.output else os.path.join(out_dir, f"output_drain3_{input_name_no_ext}.txt")

    drain3_mod.save_cluster_summary_json(summary, json_path)

    report_lines = []
    report_lines.append("==========================================================================")
    report_lines.append("🏆 ACHILLIES DRAIN3 LOG TEMPLATE MINER & SUMMARIZER REPORT")
    report_lines.append("==========================================================================")
    report_lines.append(f"• Input File          : {log_path}")
    report_lines.append(f"• Total Raw Lines     : {stats['total_lines']}")
    report_lines.append(f"• Max Line Length     : {stats['max_line_length']} char")
    report_lines.append(f"• Min Line Length     : {stats['min_line_length']} char")
    report_lines.append(f"• Avg Line Length     : {stats['avg_line_length']} char")
    report_lines.append("--------------------------------------------------------------------------")
    report_lines.append(f"• Processed Events    : {summary['total_events_processed']}")
    report_lines.append(f"• Unique Clusters     : {summary['total_unique_clusters']}")
    report_lines.append(f"• Compression Ratio   : %{summary['compression_ratio_percent']}")
    report_lines.append(f"• Drain3 Config       : Sim Threshold={args.sim_th}, Depth={args.depth}")
    report_lines.append("==========================================================================")
    report_lines.append(f"TOP {min(args.top_n, len(summary['clusters']))} MOST FREQUENT LOG TEMPLATES:")
    report_lines.append("--------------------------------------------------------------------------")

    for idx, c in enumerate(summary["clusters"][:args.top_n], 1):
        pct = (c["size_count"] / summary["total_events_processed"]) * 100.0
        report_lines.append(f"[{idx:02d}] Cluster #{c['cluster_id']:<3} | Count: {c['size_count']:<6} (%{pct:>5.2f}) | Template: {c['template']}")

    report_lines.append("==========================================================================")
    report_text = "\n".join(report_lines)

    print("\n" + report_text)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(report_text + "\n")

    print(f"\n✅ TXT raporu kaydedildi: {txt_path}")


if __name__ == "__main__":
    main()
