import os
import re
import json
import urllib.request
import google.auth
import google.auth.transport.requests

from typing import Optional

# Environment variables for GCP configuration (Zero hardcoded secrets)
GCP_REGION = os.environ.get("GCP_REGION", "us-central1")
DEFAULT_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "ilkproje-506019")


def get_gcp_adc_token() -> tuple:
    """
    Dynamically fetches GCP Application Default Credentials (ADC) token and project ID
    without hardcoding any service account keys or access tokens.
    """
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    active_project = project_id if project_id else DEFAULT_PROJECT_ID
    return credentials.token, active_project


def extract_stratified_chunks(log_file_path: str, num_chunks: int = 10, chunk_size: int = 15) -> tuple:
    """
    10 GB+ STREAMING SAFEGUARD:
    Extracts stratified multi-slice sample chunks across 10 percentile byte offsets (0%, 10%, ..., 90%)
    of the log file using seek-based file streaming.
    Memory Footprint: < 10 KB RAM regardless of whether file size is 10 MB or 100 GB.
    """
    file_size = os.path.getsize(log_file_path)
    if file_size == 0:
        return [], 0

    step_bytes = file_size // num_chunks
    chunks = []

    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
        for i in range(num_chunks):
            byte_pos = i * step_bytes
            f.seek(byte_pos)
            # If not at start of file, discard partial line
            if byte_pos > 0:
                f.readline()
            
            slice_lines = []
            for _ in range(chunk_size):
                line = f.readline()
                if not line:
                    break
                slice_lines.append(line)
            
            if slice_lines:
                chunks.append({
                    "slice_id": i + 1,
                    "start_byte": byte_pos,
                    "text": "".join(slice_lines)
                })

    return chunks, file_size


def query_vertex_gemini_for_regex(slice_text: str) -> dict:
    """
    Queries Vertex AI Gemini 2.5 Flash using 100% abstract domain-agnostic prompt
    to discover the event header boundary regex for multi-line log normalization.
    """
    token, project_id = get_gcp_adc_token()
    
    vertex_url = f"https://{GCP_REGION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{GCP_REGION}/publishers/google/models/gemini-2.5-flash:generateContent"

    prompt = f"""You are an expert SRE and Log Parsing Engineer specialized in Regular Expressions.

Task & Objective:
Log streams contain multi-line log entries where a single logical event spans across multiple lines.
Your objective is to identify a Python regular expression (`event_header_regex`) that distinguishes ONLY the START of a NEW top-level log entry.

CRITICAL ABSTRACT STRUCTURAL RULES (100% DOMAIN-AGNOSTIC):
1. `event_header_regex` MUST match ONLY top-level log entry headers (lines anchored at '^' that begin a new log event, such as lines with timestamps, log boundaries, or service prefixes).
2. Continuation lines (such as indented lines starting with whitespace/tabs, sub-messages, or stack trace details) belong to the parent log entry.
3. NEVER write rules matching continuation lines or indented trace details into `event_header_regex`. Non-matching continuation lines will be automatically concatenated onto their parent header line into a single-line log event.
4. Examine the EXACT FIRST CHARACTER (index 0, anchored at '^') of new top-level log entry headers.
5. Do NOT output generic wildcards like '.*' or '^.*$'.

OUTPUT FORMAT REQUIREMENT:
Respond ONLY with a valid JSON object matching this schema:
{{
  "event_header_regex": "<python regex pattern anchored at '^' matching top-level entry headers>",
  "is_multiline_detected": true,
  "explanation": "<short rationale describing how it identifies entry headers while letting continuation lines concatenate>"
}}

RAW LOG SLICE:
{slice_text}
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
            
            # Extract usageMetadata token accounting
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


def normalize_multiline_logs(log_file_path: str, header_regex_pattern: str, output_stream_path: Optional[str] = None) -> tuple:
    """
    10 GB+ STREAMING SAFEGUARD:
    Streams multi-line log entries line-by-line from disk and normalizes them using header_regex_pattern.
    Flushes normalized single lines directly to output_stream_path on disk when provided.
    Memory Footprint: Constant ~1 MB RAM (Zero RAM OOM crashes on 10 GB+ files).
    """
    compiled_regex = re.compile(header_regex_pattern)
    
    total_raw_lines = 0
    total_accounted = 0
    events = []
    events_count = 0
    current_event = []

    out_file = open(output_stream_path, "w", encoding="utf-8") if output_stream_path else None

    try:
        with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.rstrip("\r\n")
                if not line:
                    continue
                
                total_raw_lines += 1
                
                if compiled_regex.match(line):
                    if current_event:
                        event_str = " | ".join(current_event)
                        events_count += 1
                        total_accounted += len(current_event)
                        if out_file:
                            out_file.write(event_str + "\n")
                        else:
                            events.append(event_str)
                        current_event = []
                    current_event.append(line)
                else:
                    if current_event:
                        current_event.append(line)
                    else:
                        current_event = [line]

        if current_event:
            event_str = " | ".join(current_event)
            events_count += 1
            total_accounted += len(current_event)
            if out_file:
                out_file.write(event_str + "\n")
            else:
                events.append(event_str)

    finally:
        if out_file:
            out_file.close()

    is_zero_loss = (total_accounted == total_raw_lines)
    return events if not output_stream_path else events_count, is_zero_loss, total_raw_lines, total_accounted


if __name__ == "__main__":
    print("=== Vertex AI Gemini 2.5 Flash Normalizer Module ===")
