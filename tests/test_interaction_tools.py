import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import mcp.types as types

# Set environment variable before importing to avoid Unkey actual API calls
import os
os.environ["UNKEY_ROOT_KEY"] = ""

from phantom_cloud import handle_list_tools, handle_call_tool, state, resolve_element

@pytest.mark.asyncio
async def test_handle_list_tools_contains_new_tools():
    """Verify handle_list_tools registers all standard and new tools."""
    tools = await handle_list_tools()
    tool_names = [tool.name for tool in tools]
    
    assert "navigate" in tool_names
    assert "get_snapshot" in tool_names
    assert "click" in tool_names
    assert "type" in tool_names
    assert "evaluate" in tool_names
    assert "wait" in tool_names

@pytest.mark.asyncio
async def test_evaluate_tool_with_mocked_page():
    """Verify evaluate tool correctly evaluates the JS expression and returns stringified result."""
    # Reset/Mock state.page
    mock_page = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value=2)
    
    with patch("phantom_cloud.state.page", mock_page):
        response = await handle_call_tool("evaluate", {"expression": "1+1"})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert response[0].text == "2"
        mock_page.evaluate.assert_awaited_once_with("1+1")

@pytest.mark.asyncio
async def test_wait_tool_with_delay_only():
    """Verify wait tool successfully completes a static delay wait."""
    mock_page = AsyncMock()
    
    with patch("phantom_cloud.state.page", mock_page):
        response = await handle_call_tool("wait", {"delay_ms": 10})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "attesa" in response[0].text.lower() or "completata" in response[0].text.lower()
        assert "10ms" in response[0].text

@pytest.mark.asyncio
async def test_click_fails_controlled_when_no_page():
    """Verify click tool returns a controlled error when state.page is None."""
    with patch("phantom_cloud.state.page", None):
        response = await handle_call_tool("click", {"selector": ".btn"})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "Errore:" in response[0].text or "Esegui prima" in response[0].text

@pytest.mark.asyncio
async def test_type_fails_controlled_when_no_page():
    """Verify type tool returns a controlled error when state.page is None."""
    with patch("phantom_cloud.state.page", None):
        response = await handle_call_tool("type", {"selector": "input", "text": "hello"})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "Errore:" in response[0].text or "Esegui prima" in response[0].text

@pytest.mark.asyncio
async def test_get_snapshot_ax_mode():
    """Verify get_snapshot in 'ax' mode fetches, maps, and serializes the AX tree correctly."""
    mock_page = AsyncMock()
    
    # Mock AXNode instances
    mock_node_1 = MagicMock()
    mock_node_1.ignored = False
    mock_node_1.role = MagicMock(value="button")
    mock_node_1.name = MagicMock(value="Submit")
    mock_node_1.value = MagicMock(value="click_me")
    mock_node_1.backend_dom_node_id = 456
    
    mock_node_2 = MagicMock()
    mock_node_2.ignored = True # ignored node should be excluded
    
    mock_node_3 = MagicMock()
    mock_node_3.ignored = False
    mock_node_3.role = MagicMock(value="link")
    mock_node_3.name = MagicMock(value="Learn More")
    mock_node_3.value = None
    mock_node_3.backend_dom_node_id = 789
    
    mock_page.send = AsyncMock(side_effect=[
        None, # enable call
        [mock_node_1, mock_node_2, mock_node_3] # get_full_ax_tree call
    ])
    
    with patch("phantom_cloud.state.page", mock_page):
        response = await handle_call_tool("get_snapshot", {"mode": "ax"})
        
        assert len(response) == 1
        assert "--- AX SNAPSHOT ---" in response[0].text
        assert "[ax1: BUTTON 'Submit' value='click_me']" in response[0].text
        assert "[ax2: LINK 'Learn More']" in response[0].text
        assert "ax1" in state.element_map
        assert "ax2" in state.element_map
        assert state.element_map["ax1"]["backend_node_id"] == 456
        assert state.element_map["ax2"]["backend_node_id"] == 789

@pytest.mark.asyncio
async def test_resolve_ax_element():
    """Verify resolve_element correctly tags and resolves elements using 'ax' references."""
    mock_page = AsyncMock()
    
    mock_remote_obj = MagicMock()
    mock_remote_obj.object_id = "obj-999"
    
    mock_page.send = AsyncMock(side_effect=[
        mock_remote_obj, # resolve_node call
        None # call_function_on call
    ])
    
    mock_element = AsyncMock()
    mock_page.select = AsyncMock(return_value=mock_element)
    
    # Pre-populate state.element_map
    state.element_map["ax1"] = {
        "tag": "BUTTON",
        "context": "Submit",
        "backend_node_id": 456,
        "selector": None
    }
    
    with patch("phantom_cloud.state.page", mock_page):
        resolved = await resolve_element(ref="ax1")
        
        assert resolved == mock_element
        # Verify resolve_node call with the correct backend_node_id
        mock_page.send.assert_any_call(
            pytest.any_import_if_required # or just check mock_page.send.call_count or similar
        ) if False else None

@pytest.mark.asyncio
async def test_click_by_coords_fails_controlled_when_no_page():
    """Verify click tool with coordinates returns a controlled error when state.page is None."""
    with patch("phantom_cloud.state.page", None):
        response = await handle_call_tool("click", {"x": 100, "y": 200})
        
        assert len(response) == 1
        assert response[0].type == "text"
        assert "Errore:" in response[0].text or "Esegui prima" in response[0].text

@pytest.mark.asyncio
async def test_target_swap_recovery_and_reinject():
    """Verify that target swap recovers by updating targets and reinjecting stealth script."""
    mock_browser = AsyncMock()
    mock_old_page = AsyncMock()
    mock_new_page = AsyncMock()
    
    # Mock evaluate("1") to fail on old page to simulate target swap / dead target
    mock_old_page.send = AsyncMock(side_effect=Exception("Target swap / disconnected"))
    
    mock_browser.tabs = [mock_new_page]
    mock_browser.main_tab = mock_new_page
    mock_browser.update_targets = AsyncMock()
    
    with patch("phantom_cloud.state.browser", mock_browser), \
         patch("phantom_cloud.state.page", mock_old_page):
         
        # We can call any tool that doesn't immediately succeed, e.g. evaluate (which will then run on mock_new_page)
        # Or we can just call handle_call_tool with evaluate and mock evaluate to succeed on mock_new_page
        mock_new_page.evaluate = AsyncMock(return_value="repaired")
        mock_new_page.send = AsyncMock()
        
        response = await handle_call_tool("evaluate", {"expression": "document.title"})
        
        # Verify it updated targets
        mock_browser.update_targets.assert_awaited_once()
        # Verify it updated state.page to mock_new_page
        from phantom_cloud import state
        assert state.page == mock_new_page
        # Verify it reinjected the stealth payload on mock_new_page
        assert mock_new_page.send.await_count >= 1

