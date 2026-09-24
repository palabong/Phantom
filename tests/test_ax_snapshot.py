import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os
os.environ["UNKEY_ROOT_KEY"] = ""

from phantom_cloud import handle_call_tool, state

@pytest.mark.asyncio
async def test_get_snapshot_html_mode_when_no_page():
    """Verify get_snapshot in html mode does not raise when page is None but returns a controlled error."""
    with patch("phantom_cloud.state.page", None):
        response = await handle_call_tool("get_snapshot", {"mode": "html"})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "Errore:" in response[0].text or "Esegui prima" in response[0].text

@pytest.mark.asyncio
async def test_get_snapshot_ax_mode_when_no_page():
    """Verify get_snapshot in ax mode does not raise when page is None but returns a controlled error."""
    with patch("phantom_cloud.state.page", None):
        response = await handle_call_tool("get_snapshot", {"mode": "ax"})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "Errore:" in response[0].text or "Esegui prima" in response[0].text

@pytest.mark.asyncio
async def test_ax_serialization_with_synthetic_minimal_tree():
    """Verify ax serialization successfully formats a minimal synthetic tree into formatted text."""
    mock_page = AsyncMock()
    
    # Mock a single synthetic AXNode
    mock_node = MagicMock()
    mock_node.ignored = False
    mock_node.role = MagicMock(value="button")
    mock_node.name = MagicMock(value="Click Me")
    mock_node.value = MagicMock(value="action_value")
    mock_node.backend_dom_node_id = 123
    
    mock_page.send = AsyncMock(side_effect=[
        None, # for accessibility.enable
        [mock_node] # for accessibility.get_full_ax_tree
    ])
    
    with patch("phantom_cloud.state.page", mock_page):
        response = await handle_call_tool("get_snapshot", {"mode": "ax"})
        
        assert len(response) == 1
        assert "--- AX SNAPSHOT ---" in response[0].text
        assert "[ax1: BUTTON 'Click Me' value='action_value']" in response[0].text
        assert "--- END SNAPSHOT ---" in response[0].text
        
        # Verify element mapping was written correctly
        assert "ax1" in state.element_map
        assert state.element_map["ax1"]["tag"] == "BUTTON"
        assert state.element_map["ax1"]["context"] == "Click Me"
        assert state.element_map["ax1"]["backend_node_id"] == 123
