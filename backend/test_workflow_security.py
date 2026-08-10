import sys
import os
from unittest.mock import MagicMock

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock langchain libraries to prevent loading Ollama/FAISS during testing
sys.modules['langchain_ollama'] = MagicMock()
sys.modules['langchain_community.vectorstores'] = MagicMock()
sys.modules['langchain_community.document_loaders'] = MagicMock()
sys.modules['langchain_text_splitters'] = MagicMock()

# Also mock security's encryptor so we don't depend on Fernet key validation during orchestrator init
import security
security.encryptor = MagicMock()

from agents.orchestrator import AgentOrchestrator
from agents.base_agent import AgentState

print("Starting CVE-7 Workflow Security Verification Tests...\n" + "="*60)

orchestrator = AgentOrchestrator()

# Set up test data
valid_steps = [
    # (Agent, Action, Params)
    {"agent": "weather", "action": "check", "params": {"query": "Bogor"}},
    {"agent": "farm", "action": "create_plan", "params": {"crop": "padi", "area_size": 1.0, "location": "Bogor"}},
    {"agent": "knowledge", "action": "get_guidance", "params": {"topic": "padi"}},
]

malicious_steps = [
    # Call a valid method on a non-authorized agent
    {"agent": "weather", "action": "monitor_farmer", "params": {"farmer_id": "default"}},
    # Attempt to call internal attributes / dunders (arbitrary getattr)
    {"agent": "weather", "action": "__class__", "params": {}},
    # Attempt to call non-whitelisted dangerous method
    {"agent": "knowledge", "action": "clear_memory", "params": {}},
]

passed_tests = 0
total_tests = len(valid_steps) + len(malicious_steps)

# 1. Test allowed steps
print("\n--- Testing Valid Whitelisted Workflow Actions ---")
for step in valid_steps:
    agent_name = step["agent"]
    action = step["action"]
    params = step["params"]
    
    print(f"Executing: {agent_name}.{action} with {params}")
    try:
        agent = orchestrator.agents.get(agent_name)
        context = orchestrator._get_farmer_context("default")
        result = orchestrator._execute_agent_action(agent, action, params, context)
        print(f"  [OK] Success. Action executed without PermissionError.")
        passed_tests += 1
    except PermissionError as e:
        print(f"  [FAIL] Action was blocked, but should have been allowed: {e}")
    except Exception as e:
        # Other exceptions are fine (e.g. from mock/missing dependency), as long as it wasn't a PermissionError
        print(f"  [OK] Success. Executed action, caught acceptable mock/dependency error: {e}")
        passed_tests += 1

# 2. Test blocked steps
print("\n--- Testing Malicious/Blocked Workflow Actions ---")
for step in malicious_steps:
    agent_name = step["agent"]
    action = step["action"]
    params = step["params"]
    
    print(f"Executing: {agent_name}.{action} with {params}")
    try:
        agent = orchestrator.agents.get(agent_name)
        context = orchestrator._get_farmer_context("default")
        result = orchestrator._execute_agent_action(agent, action, params, context)
        print("  [FAIL] Danger! Action was allowed when it should have been blocked.")
    except PermissionError as e:
        print(f"  [OK] Success. Action was correctly blocked: {e}")
        passed_tests += 1
    except Exception as e:
        print(f"  [FAIL] Unexpected exception type (expected PermissionError): {e}")

print("="*60)
print(f"Verification Completed: {passed_tests}/{total_tests} tests passed.")

if passed_tests == total_tests:
    sys.exit(0)
else:
    sys.exit(1)
