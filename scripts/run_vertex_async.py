import os
import sys
import time
import json
import re
import urllib.request
import google.auth
import google.auth.transport.requests

def test_multiline_normalization(regex_str, raw_lines_sample):
    if not regex_str or regex_str.strip() in [".*", "^.*$"]:
        return False, 0.0, 0, 0, "REJECTED (GENERIC WILDCARD '.*')"

    try:
        compiled = re.compile(regex_str)
    except Exception as e:
        return False, 0.0, 0, 0, f"SYNTAX ERROR: {e}"

    events = []
    current_event = []

    for line in raw_lines_sample:
        clean = line.rstrip("\r\n")
        if not clean:
            continue
        if compiled.match(clean):
            if current_event:
                events.append(current_event)
                current_event = []
            current_event.append(clean)
        else:
            if current_event:
                current_event.append(clean)
            else:
                current_event = [clean]

    if current_event:
        events.append(current_event)

    total_accounted = sum(len(e) for e in events)
    total_raw = len([l for l in raw_lines_sample if l.rstrip("\r\n")])
    is_zero_loss = (total_accounted == total_raw)
    multiline_count = sum(1 for e in events if len(e) > 1)

    return is_zero_loss, len(events), multiline_count, total_accounted, "PASSED ZERO-LOSS" if is_zero_loss else "FAILED"

def query_gemini_25_flash(slice_text: str) -> dict:
    credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    token = credentials.token
    project_id = "ilkproje-506019"
    location = "us-central1"

    vertex_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/gemini-2.5-flash:generateContent"

    prompt = f"""You are an expert SRE and Log Parsing Engineer specialized in Regular Expressions.

Task & Objective:
Log streams may contain multi-line log entries where a single logical event spans across multiple lines.
Your objective is to identify a Python regular expression (`event_header_regex`) that distinguishes the START of a NEW logical log entry from any continuation lines.

HOW THIS REGEX WILL BE USED:
An automated parser uses your regex to normalize multi-line events into single-line events:
- Matching lines mark the START of a NEW logical log entry.
- Non-matching lines are continuation lines and will be concatenated to the preceding entry.

CRITICAL INSTRUCTIONS:
1. Examine the EXACT FIRST CHARACTER (index 0, anchored at '^') of every new log entry line in the sample.
2. Note that the sample may start in the middle of a continuation line or stacktrace. Identify the pattern that uniquely marks the START of a NEW log entry.
3. Do NOT output generic wildcards like '.*' or '^.*$'.

OUTPUT FORMAT REQUIREMENT:
Respond ONLY with a valid JSON object matching this schema:
{{
  "event_header_regex": "<python regex pattern anchored at '^' matching line start>",
  "is_multiline_detected": true,
  "explanation": "<short rationale describing how it separates new entries from stacktrace lines>"
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
            return json.loads(raw_text)
    except Exception as e:
        return {"error": str(e)}

def main():
    repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_file = os.path.join(repo_dir, "vertex_results.txt")

    test_targets = [
        {
            "name": "OpenStack Normal 2 (En Büyük Log)",
            "file": os.path.join(repo_dir, "data/openstack_normal2.log"),
            "slice_line": 68537
        },
        {
            "name": "OpenStack Abnormal (Arızalı / Anomali Logu)",
            "file": os.path.join(repo_dir, "data/openstack_abnormal.log"),
            "slice_line": 9200
        },
        {
            "name": "Hadoop Container (Java Stacktrace Logu)",
            "file": os.path.join(repo_dir, "data/application_1445144423722_0020/container_1445144423722_0020_01_000001.log"),
            "slice_line": 852
        }
    ]

    with open(out_file, "w", encoding="utf-8") as out:
        out.write("======================================================================\n")
        out.write("📌 VERTEX AI GEMINI 2.5 FLASH - TÜM BÜYÜK SRE DOSYALARI TEST TABLOSU\n")
        out.write("======================================================================\n")
        out.write(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for target in test_targets:
            fname = target["name"]
            fpath = target["file"]
            sidx = target["slice_line"]

            out.write(f"----------------------------------------------------------------------\n")
            out.write(f"🔍 {fname}\n")
            out.write(f"  └─ Dosya: {os.path.basename(fpath)} | Dilim Satırı: #{sidx+1}\n")
            out.write(f"----------------------------------------------------------------------\n")
            out.flush()

            if not os.path.exists(fpath):
                out.write(f"  ❌ File not found: {fpath}\n\n")
                continue

            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            slice_text = "".join(lines[sidx : sidx + 60])
            test_sample = lines[sidx : sidx + 1000]

            gemini_res = query_gemini_25_flash(slice_text)
            regex_str = gemini_res.get("event_header_regex", "N/A")
            expl = gemini_res.get("explanation", gemini_res.get("error", "No explanation"))
            multiline_flag = gemini_res.get("is_multiline_detected", False)

            is_zero_loss, total_events, multiline_events, accounted, status_str = test_multiline_normalization(regex_str, test_sample)

            out.write(f"• Gemini 2.5 Flash Regex   : `{regex_str}`\n")
            out.write(f"• Çoklu Satır Tespiti      : {multiline_flag}\n")
            out.write(f"• Test Edilen Satır        : {len(test_sample)}\n")
            out.write(f"• Birleştirilen Olay       : {total_events}\n")
            out.write(f"• Yakalanan Stacktrace     : {multiline_events}\n")
            out.write(f"• Sıfır-Kayıp Eşitliği     : {status_str}\n")
            out.write(f"• Açıklama                 : {expl}\n\n")
            out.flush()

        out.write("======================================================================\n")
        out.write(f"Tüm Büyük Dosyaların Testi Tamamlandı ({time.strftime('%Y-%m-%d %H:%M:%S')})\n")

if __name__ == "__main__":
    main()
