#!/usr/bin/env python3
"""
MCP Model Comparison: jan-nano vs Qwen 35B
Tests performance, quality, and capabilities
"""

import time
import json
import subprocess
import sys

MODELS = {
    "jan-nano": "huihui_ai/jan-nano-abliterated:latest",
    "qwen35b": "qwen3.5:35b-a3b-coding-nvfp4"
}

def generate_response(model, prompt, timeout=120):
    """Generate response and measure performance using curl"""
    start = time.time()

    cmd = [
        "curl", "-s", "http://localhost:11434/api/generate",
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"model": model, "prompt": prompt, "stream": False}),
        "--max-time", str(timeout)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        elapsed = time.time() - start

        if result.returncode == 0:
            data = json.loads(result.stdout)
            response_text = data.get("response", "")
            tokens = data.get("eval_count", 0)
            eval_rate = data.get("eval_count", 0) / (data.get("eval_duration", 1) / 1e9) if data.get("eval_duration") else 0

            return {
                "success": True,
                "response": response_text,
                "time": elapsed,
                "tokens": tokens,
                "tokens_per_second": round(eval_rate, 1) if eval_rate else 0,
                "truncated": data.get("done_reason") == "length"
            }
        else:
            return {"success": False, "error": f"Curl error: {result.returncode}", "time": elapsed}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout", "time": timeout}
    except Exception as e:
        return {"success": False, "error": str(e), "time": time.time() - start}

def run_tests():
    print("=" * 70)
    print("MCP MODEL COMPARISON: jan-nano vs Qwen 35B")
    print("=" * 70)

    results = {model: {"tests": []} for model in MODELS}

    tests = [
        {
            "name": "Code Generation (Python)",
            "prompt": "Write a Python function to check if a string is a palindrome. Only return the code.",
            "timeout": 60
        },
        {
            "name": "Code Generation (JavaScript)",
            "prompt": "Write a JavaScript function to debounce a button click. Only return the code.",
            "timeout": 60
        },
        {
            "name": "General Knowledge",
            "prompt": "What is Model Context Protocol (MCP) in one sentence?",
            "timeout": 30
        },
        {
            "name": "MCP Context",
            "prompt": "Explain how MCP reduces LLM token usage in 2 sentences.",
            "timeout": 30
        },
        {
            "name": "Technical Question",
            "prompt": "What are the benefits of using local LLMs like Ollama for privacy?",
            "timeout": 90
        }
    ]

    for test in tests:
        print(f"\n{'='*70}")
        print(f"TEST: {test['name']}")
        print(f"{'='*70}")

        for model_name, model_id in MODELS.items():
            print(f"\n[{model_name}] ", end="", flush=True)
            result = generate_response(model_id, test["prompt"], test["timeout"])

            if result["success"]:
                status = "✅" if not result.get("truncated") else "⚠️"
                print(f"{status} {result['time']:.1f}s | {result['tokens']} tokens | {result['tokens_per_second']:.1f} t/s")
                response_preview = result['response'][:200].replace('\n', ' ')
                print(f"   → {response_preview}...")
                results[model_name]["tests"].append({
                    "name": test["name"],
                    **result
                })
            else:
                print(f"❌ Error: {result.get('error', 'Unknown')}")
                results[model_name]["tests"].append({
                    "name": test["name"],
                    "success": False,
                    "error": result.get("error")
                })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY & RECOMMENDATIONS")
    print("=" * 70)

    for model_name in MODELS:
        tests_passed = sum(1 for t in results[model_name]["tests"] if t.get("success"))
        successful_tests = [t for t in results[model_name]["tests"] if t.get("success")]
        avg_time = sum(t["time"] for t in successful_tests) / max(len(successful_tests), 1)
        avg_tps = sum(t["tokens_per_second"] for t in successful_tests if t.get("tokens_per_second")) / max(len(successful_tests), 1)

        print(f"\n{model_name.upper()}:")
        print(f"  Tests Passed: {tests_passed}/{len(tests)}")
        print(f"  Avg Response Time: {avg_time:.1f}s")
        print(f"  Avg Tokens/Second: {avg_tps:.1f} t/s")

    # Comparison
    print("\n" + "-" * 70)
    print("COMPARISON")
    print("-" * 70)

    jan_results = results["jan-nano"]["tests"]
    qwen_results = results["qwen35b"]["tests"]

    jan_avg_time = sum(t["time"] for t in jan_results if t.get("success")) / max(sum(1 for t in jan_results if t.get("success")), 1)
    qwen_avg_time = sum(t["time"] for t in qwen_results if t.get("success")) / max(sum(1 for t in qwen_results if t.get("success")), 1)

    print(f"\nSpeed Winner: {'jan-nano' if jan_avg_time < qwen_avg_time else 'qwen35b'} ({min(jan_avg_time, qwen_avg_time):.1f}s vs {max(jan_avg_time, qwen_avg_time):.1f}s)")
    print(f"Speed Advantage: {abs(jan_avg_time - qwen_avg_time) / max(jan_avg_time, qwen_avg_time) * 100:.0f}% faster")

    jan_tps = sum(t["tokens_per_second"] for t in jan_results if t.get("success") and t.get("tokens_per_second")) / max(sum(1 for t in jan_results if t.get("success") and t.get("tokens_per_second")), 1)
    qwen_tps = sum(t["tokens_per_second"] for t in qwen_results if t.get("success") and t.get("tokens_per_second")) / max(sum(1 for t in qwen_results if t.get("success") and t.get("tokens_per_second")), 1)

    print(f"\nToken Speed Winner: {'jan-nano' if jan_tps > qwen_tps else 'qwen35b'} ({max(jan_tps, qwen_tps):.1f} t/s)")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    run_tests()
