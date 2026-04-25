import os
import pytest
from blocklink.adapters.ipfs.tools import upload_file_ipfs

def test_hardcoded_password_removed():
    tools_path = os.path.join("blocklink", "adapters", "ipfs", "tools.py")
    with open(tools_path, "r", encoding="utf-8") as f:
        content = f.read()

    # The hardcoded password that was previously there
    bad_password = "dirrk2938884jMMFhs01"

    assert bad_password not in content, f"Hardcoded password '{bad_password}' still found in {tools_path}"
    assert "os.getenv(\"IPFS_PASSWORD\")" in content, "os.getenv lookup for IPFS_PASSWORD not found"

def test_upload_file_ipfs_raises_if_no_env(tmp_path):
    # Ensure IPFS_PASSWORD is not set
    if "IPFS_PASSWORD" in os.environ:
        del os.environ["IPFS_PASSWORD"]

    test_file = tmp_path / "test.txt"
    test_file.write_text("hello")

    with pytest.raises(ValueError, match="IPFS_PASSWORD environment variable is not set"):
        upload_file_ipfs(str(test_file), "http://localhost:8000")

def test_imports_correctly():
    # This test ensures that the module can be imported and doesn't have NameErrors
    import blocklink.adapters.ipfs.tools
    assert hasattr(blocklink.adapters.ipfs.tools, 'upload_file_ipfs')
