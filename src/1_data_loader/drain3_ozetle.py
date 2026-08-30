import os
import json
import argparse
from drain3 import TemplateMiner
from drain3.template_miner_config import TemplateMinerConfig


def analyze_file_structural_metrics(raw_lines: list) -> dict:
    """
    Performs structural checks on input log lines:
    - Calculates maximum line character length
    - Calculates minimum non-empty line character length
    - Calculates average line character length
    """
    if not raw_lines:
        return {
            "total_lines": 0,
            "max_line_length": 0,
            "min_line_length": 0,
            "avg_line_length": 0.0
        }

    line_lengths = [len(l) for l in raw_lines]
    max_len = max(line_lengths)
    min_len = min(line_lengths)
    avg_len = round(sum(line_lengths) / len(line_lengths), 2)

    return {
        "total_lines": len(raw_lines),
        "max_line_length": max_len,
        "min_line_length": min_len,
        "avg_line_length": avg_len
    }


def run_drain3_clustering(
    events: list,
    sim_th: float = 0.5,
    depth: int = 4
) -> dict:
    """
    Generic Domain-Agnostic Log Summarizer using Drain3 Template Mining.
    
    Accepts any list of normalized single-line log event strings.
    Extracts dynamic wildcards (<*>), groups repeating log patterns into unique clusters,
    and ranks them by occurrence count.
    
    :param events: List of single-line log event strings.
    :param sim_th: Similarity threshold for Drain3 matching (default 0.5).
    :param depth: Parse tree depth for Drain3 (default 4).
    :return: Dictionary containing summary metrics and sorted cluster list.
    """
    config = TemplateMinerConfig()
    config.drain_target_depth = depth
    config.drain_sim_th = sim_th
    
    miner = TemplateMiner(config=config)

    for event in events:
        miner.add_log_message(event)

    clusters = []
    for cluster in miner.drain.clusters:
        clusters.append({
            "cluster_id": cluster.cluster_id,
            "size_count": cluster.size,
            "template": cluster.get_template(),
            "sample_log": cluster.get_template()
        })

    # Sort clusters descending by frequency (most frequent pattern first)
    clusters.sort(key=lambda x: x["size_count"], reverse=True)

    total_events = len(events)
    total_clusters = len(clusters)
    compression_ratio = (1.0 - (total_clusters / max(total_events, 1))) * 100.0

    structural_stats = analyze_file_structural_metrics(events)

    return {
        "file_structural_stats": structural_stats,
        "total_events_processed": total_events,
        "total_unique_clusters": total_clusters,
        "compression_ratio_percent": round(compression_ratio, 2),
        "drain3_config": {
            "sim_th": sim_th,
            "depth": depth
        },
        "clusters": clusters
    }


def save_cluster_summary_json(summary_dict: dict, output_filepath: str) -> None:
    """Saves the cluster summary dictionary to a formatted JSON file."""
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(summary_dict, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON özet raporu kaydedildi: {output_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="achillies Generic Drain3 Log Template Miner & Summarizer")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input text/log file (one event per line)")
    parser.add_argument("--sim-th", type=float, default=0.5, help="Drain3 similarity threshold (default: 0.5)")
    parser.add_argument("--depth", type=int, default=4, help="Drain3 parse tree depth (default: 4)")
    parser.add_argument("--top-n", type=int, default=10, help="Print top N most frequent clusters to stdout (default: 10)")
    parser.add_argument("--json-out", "-j", type=str, default=None, help="Optional output JSON summary path")
    parser.add_argument("--output", "-o", type=str, default=None, help="Optional output TXT report path")

    args = parser.parse_args()
    log_path = os.path.abspath(args.input)

    if not os.path.exists(log_path):
        print(f"❌ Target log file not found: {log_path}")
        exit(1)

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = [l.strip() for l in f if l.strip()]

    summary = run_drain3_clustering(raw_lines, sim_th=args.sim_th, depth=args.depth)
    stats = summary["file_structural_stats"]

    # Derive default output paths if omitted
    input_base = os.path.basename(log_path)
    input_name_no_ext = os.path.splitext(input_base)[0]
    out_dir = os.path.dirname(log_path)

    json_path = os.path.abspath(args.json_out) if args.json_out else os.path.join(out_dir, f"summary_drain3_{input_name_no_ext}.json")
    txt_path = os.path.abspath(args.output) if args.output else os.path.join(out_dir, f"output_drain3_{input_name_no_ext}.txt")

    save_cluster_summary_json(summary, json_path)

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
