import json, os

path = "backend/benchmark_results.json"
if not os.path.exists(path):
    print("File not found yet.")
else:
    with open(path, "r", encoding="utf8") as f:
        data = json.load(f)
    print(f"Total queries completed: {len(data)}/100")
    for i, d in enumerate(data):
        std = "OK" if not d.get("standard_rag","").startswith("Error") else "FAIL"
        sta = "OK" if not d.get("static_multi_tool","").startswith("Error") else "FAIL"
        agt = "OK" if not d.get("agentic_rag","").startswith("Error") else "FAIL"
        print(f"  [{i+1:3d}] std={std} | static={sta} | agentic={agt}")
