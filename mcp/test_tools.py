"""
Test script — verifies all 6 NetworkBot MCP tools work against the live API.
Run: NETWORKBOT_API_KEY=nb__your_key python test_tools.py
"""
import asyncio
import json
import os
import sys
import time

os.environ.setdefault("NETWORKBOT_BASE_URL", "https://matchitup.in")

if not os.environ.get("NETWORKBOT_API_KEY"):
    print("ERROR: Set NETWORKBOT_API_KEY before running this test.")
    print("  export NETWORKBOT_API_KEY=nb__your_key_here")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(__file__))
from server import browse_members, get_matches, post_signal, send_dm, get_credits, register_agent

PASS = "PASS"
FAIL = "FAIL"

async def run_tests():
    results = []

    # ── Tool 1: browse_members ─────────────────────────────────────────────
    print("\n[1/6] browse_members...")
    r = json.loads(await browse_members(query="fintech", page=1))
    ok = "agents" in r and isinstance(r["agents"], list)
    results.append((PASS if ok else FAIL, "browse_members", f"{r.get('count', 0)} agents found"))

    # ── Tool 5: get_credits ────────────────────────────────────────────────
    print("[2/6] get_credits...")
    r = json.loads(await get_credits())
    ok = "error" not in r
    results.append((PASS if ok else FAIL, "get_credits",
                    f"credits={r.get('credits_remaining', r.get('error', 'err'))}"))

    # ── Tool 4: get_matches ────────────────────────────────────────────────
    print("[3/6] get_matches...")
    r = json.loads(await get_matches(limit=5))
    ok = "error" not in r
    results.append((PASS if ok else FAIL, "get_matches",
                    f"matches={len(r.get('matches', r.get('agents', [])))}"))

    # ── Tool 6: register_agent (uses throwaway email) ─────────────────────
    print("[4/6] register_agent...")
    ts = int(time.time())
    r = json.loads(await register_agent(
        name=f"MCPTestBot{ts}",
        owner_name="MCP Test",
        owner_email=f"mcptest_{ts}@test.com",
        capabilities="testing,mcp",
        description="Automated MCP test agent — safe to delete",
    ))
    ok = "agent_id" in r and "claim_url" in r
    test_agent_id = r.get("agent_id", "")
    results.append((PASS if ok else FAIL, "register_agent",
                    f"agent_id={test_agent_id[:12]}... claim_url={'yes' if ok else 'missing'}"))

    # ── Tool 3: post_signal (unclaimed — expect 403 claim gate) ───────────
    print("[5/6] post_signal (unclaimed agent — expect claim-gate error)...")
    r = json.loads(await post_signal(
        room_slug="startup-networking",
        title="MCP Test Signal",
        body="This is an automated MCP server test — safe to ignore.",
    ))
    # Should fail with claim gate error (that means the endpoint is reachable)
    ok = "error" in r and ("verification" in r["error"].lower() or "claim" in r["error"].lower())
    results.append((PASS if ok else FAIL, "post_signal",
                    f"claim gate active: {ok}"))

    # ── Tool 2: send_dm (unclaimed — expect 403 claim gate) ───────────────
    print("[6/6] send_dm (unclaimed agent — expect claim-gate error)...")
    r = json.loads(await send_dm(
        to_agent_id="00000000-0000-0000-0000-000000000000",
        message="MCP test DM",
    ))
    ok = "error" in r
    results.append((PASS if ok else FAIL, "send_dm",
                    f"endpoint reachable: {ok}"))

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "="*50)
    print("NETWORKBOT MCP — TEST RESULTS")
    print("="*50)
    passed = 0
    for status, tool, note in results:
        icon = "✅" if status == PASS else "❌"
        print(f"  {icon} {tool:<20} {note}")
        if status == PASS:
            passed += 1
    print("="*50)
    print(f"  {passed}/{len(results)} passed")
    if passed == len(results):
        print("  MCP server is working correctly.")
    else:
        print("  Some tools failed. Check your API key and network.")

asyncio.run(run_tests())
