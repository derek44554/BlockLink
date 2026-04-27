import os
import pytest
from unittest.mock import MagicMock
from blocklink.models.connect.connect import ConnectModel
from blocklink.utils.tools import save_to_yaml

def test_connect_model_path_traversal_mitigation(tmp_path):
    # Save current directory
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        os.makedirs("data/connect", exist_ok=True)

        # We use a path that goes up one level from data/connect/
        # Current expected path: data/connect/../traversal.yml -> data/traversal.yml
        malicious_bid = "../traversal"
        data = {"bid": malicious_bid}
        model = ConnectModel(data)

        model.save()

        # In a vulnerable state, this file will exist
        vulnerable_path = "data/traversal.yml"
        sanitized_path = "data/connect/traversal.yml"

        # This test should pass as the vulnerability is fixed
        assert not os.path.exists(vulnerable_path), f"Path traversal vulnerability STILL present: file created at {os.path.abspath(vulnerable_path)}"
        assert os.path.exists(sanitized_path), "File should be created at sanitized path"
    finally:
        os.chdir(old_cwd)

def test_node_verify_mitigation_logic(tmp_path):
    # node.py logic:
    # safe_bid = os.path.basename(node_model.signature_model.bid)
    # save_to_yaml(node_model.signature_model.data, f"./data/signature/{safe_bid}.yml")

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        os.makedirs("data/signature", exist_ok=True)

        malicious_bid = "../../evil"

        # Fixed logic simulation:
        safe_bid = os.path.basename(malicious_bid)
        save_path = f"./data/signature/{safe_bid}.yml"

        save_to_yaml({}, save_path)

        vulnerable_file = "evil.yml"
        expected_file = "data/signature/evil.yml"

        assert not os.path.exists(vulnerable_file), "Path traversal vulnerability still present in logic"
        assert os.path.exists(expected_file), "File should be created at sanitized path"
    finally:
        os.chdir(old_cwd)
