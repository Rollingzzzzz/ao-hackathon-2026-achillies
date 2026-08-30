import os
import re
import json
import urllib.request
import google.auth
import google.auth.transport.requests

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
    Extracts stratified multi-slice sample chunks across 10 percentile points (0%, 10%, 20%, ..., 90%)
    of the log file to maximize representation of heterogeneous log formats.
    """
    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()

    total_lines = len(all_lines)
    step = max(1, total_lines // num_chunks)
    positions = [i * step for i in range(num_chunks)]

    chunks = []
    for idx, pos in enumerate(positions, 1):
        lines_slice = all_lines[pos : pos + chunk_size]
        slice_text = "".join(lines_slice)
        chunks.append({
            "slice_id": idx,
            "start_line": pos,
            "text": slice_text
        })

    return chunks, total_lines


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


def normalize_multiline_logs(log_file_path: str, header_regex_pattern: str) -> tuple:
    """
    Normalizes multi-line log entries into single-line events using the discovered regex.
    Performs 100% zero-loss accounting verification.
    """
    compiled_regex = re.compile(header_regex_pattern)
    
    with open(log_file_path, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = [l.rstrip("\r\n") for l in f.readlines() if l.rstrip("\r\n")]

    events = []
    current_event = []

    for line in raw_lines:
        if compiled_regex.match(line):
            if current_event:
                events.append(" | ".join(current_event))
                current_event = []
            current_event.append(line)
        else:
            if current_event:
                current_event.append(line)
            else:
                current_event = [line]

    if current_event:
        events.append(" | ".join(current_event))

    total_accounted = sum(len(e.split(" | ")) for e in events)
    is_zero_loss = (total_accounted == len(raw_lines))

    return events, is_zero_loss, len(raw_lines), total_accounted


if __name__ == "__main__":
    print("=== Vertex AI Gemini 2.5 Flash Normalizer Module ===")
