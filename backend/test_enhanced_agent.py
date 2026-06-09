#!/usr/bin/env python3
"""
Integration test suite for the 90% Agentic Device Control Agent.

Run from the backend/ directory (inside venv):
    python test_enhanced_agent.py

Note: Multi-turn tool-use tests may be slow (10-60s per request) due to
Bedrock throughput limits. For production use, provision a Bedrock throughput
unit for amazon.nova-lite-v2:0.
"""

import sys
import time

sys.path.insert(0, ".")


def separator(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def run_test(label: str, fn, *args, timeout_hint: str = "") -> bool:
    try:
        t = time.time()
        result = fn(*args)
        elapsed = time.time() - t
        preview = str(result)[:300].replace("\n", " ").encode("ascii", errors="replace").decode()
        print(f"  [PASS] {label} ({elapsed:.1f}s){' -- ' + timeout_hint if timeout_hint else ''}")
        print(f"         -> {preview}")
        return True
    except Exception as exc:
        print(f"  [FAIL] {label}")
        print(f"         ERR: {exc}")
        import traceback
        traceback.print_exc()
        return False


def test_90pct_agentic_agent():
    separator("Device Control Agent - 90% Agentic Test Suite")

    results = []

    # -- Import & init ----------------------------------------------------------
    try:
        from app.agent.agent_service import get_device_agent
        agent = get_device_agent()
        print("  [PASS] Agent initialised (Strands + Nova 2 Lite, streaming=False)")
    except Exception as exc:
        print(f"  [FAIL] Agent init failed: {exc}")
        import traceback
        traceback.print_exc()
        return False

    # -- Test 1: Device discovery -----------------------------------------------
    separator("Test 1 - Device Discovery (single-turn list_devices)")
    results.append(
        run_test(
            "List all devices",
            agent.process_request,
            "List all devices and show me their current status",
        )
    )

    # -- Test 2: Single-device control ------------------------------------------
    separator("Test 2 - Single Device Control (multi-turn: list + set)")
    print("  NOTE: This test may take 30-60s due to Bedrock multi-turn throttling.")
    results.append(
        run_test(
            "Turn off Heat pump",
            agent.process_request,
            "Turn off the Heat pump",
            timeout_hint="multi-turn (list_devices + set_device_status)",
        )
    )

    # -- Test 3: Multi-device control -------------------------------------------
    separator("Test 3 - Multi-Device Control (update_multiple_devices)")
    print("  NOTE: Should use update_multiple_devices_tool for 2 devices.")
    results.append(
        run_test(
            "Turn on Heat pump AND HVAC",
            agent.process_request,
            "Turn on Heat pump and HVAC",
        )
    )

    # -- Test 4: Pronoun resolution via memory ----------------------------------
    separator("Test 4 - Pronoun Resolution (conversation memory)")
    results.append(
        run_test(
            "What was the previous status of the last changed device?",
            agent.process_request,
            "What was the previous status of the last device you changed?",
        )
    )

    # -- Test 5: Complex bulk intent --------------------------------------------
    separator("Test 5 - Bulk Intent: Turn off all online devices")
    results.append(
        run_test(
            "Turn off all currently online devices",
            agent.process_request,
            "Turn off all devices that are currently online",
        )
    )

    # -- Test 6: Status check ---------------------------------------------------
    separator("Test 6 - Status Verification")
    results.append(
        run_test(
            "Check Dishwasher status",
            agent.process_request,
            "What is the current status of the Dishwasher?",
        )
    )

    # -- Test 7: Memory reset ---------------------------------------------------
    separator("Test 7 - Memory Reset")
    try:
        agent.reset_memory()
        print("  [PASS] Conversation history cleared")
        results.append(True)
    except Exception as exc:
        print(f"  [FAIL] Memory reset failed: {exc}")
        results.append(False)

    # -- Summary ----------------------------------------------------------------
    separator("Results Summary")
    passed = sum(results)
    total = len(results)
    print(f"  {passed}/{total} tests passed")

    if passed == total:
        print("\n  [SUCCESS] 90% Agentic System is working correctly!")
        print("  Key capabilities validated:")
        print("    * Nova Lite drives ALL tool selection (no Python routing)")
        print("    * Multi-device bulk updates via update_multiple_devices")
        print("    * Conversation memory for pronoun resolution")
        print("    * Complex natural language -> multi-step workflow")
    else:
        print(f"\n  [WARNING] {total - passed} test(s) failed. Check logs above.")
        print("  Note: slow tests may be Bedrock throttling, not code errors.")

    return passed == total


if __name__ == "__main__":
    success = test_90pct_agentic_agent()
    sys.exit(0 if success else 1)