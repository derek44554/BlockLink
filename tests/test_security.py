import os
import pytest
from blocklink.routers.node import node_verify
from blocklink.models.connect.connect import ConnectModel
from unittest.mock import MagicMock, patch

def test_bid_sanitization():
    # Test path traversal prevention in ConnectModel
    data = {"bid": "../../../etc/passwd"}
    model = ConnectModel(data)
    with patch("blocklink.models.connect.connect.save_to_yaml") as mock_save:
        model.save()
        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        assert "passwd.yml" in args[1]
        assert ".." not in args[1]

@pytest.mark.asyncio
async def test_node_verify_sanitization():
    # Test path traversal prevention in node_verify
    mock_websocket = MagicMock()
    mock_ins_open = MagicMock()
    mock_ins_open.sender = "attacker"
    mock_ins_open.data = {"v": "dummy"}

    mock_node_model = MagicMock()
    mock_node_model.encryption_key = b"dummy_key"
    mock_node_model.signature_model.bid = "../../evil"
    mock_node_model.signature_model.data = {"some": "data"}

    with patch("blocklink.routers.node.NodeManager") as mock_nm,          patch("blocklink.routers.node.decrypt_with_symmetric_key_base64", return_value=b"ok"),          patch("blocklink.routers.node.save_to_yaml") as mock_save,          patch("blocklink.routers.node.ConnectModel"),          patch("blocklink.routers.node.ConnectManager"),          patch("blocklink.routers.node.send_ins_node_info"):

        mock_nm.return_value.not_active_node = {"attacker": mock_node_model}

        from blocklink.routers.node import node_verify
        await node_verify(mock_websocket, mock_ins_open)

        mock_save.assert_called_once()
        args, _ = mock_save.call_args
        assert "evil.yml" in args[1]
        assert ".." not in args[1]
