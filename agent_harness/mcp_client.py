"""MCP Client for Agent Harness.

Client for interacting with the IA Hoteles MCP (Model Context Protocol) server.
v3.1: Fixed nested event loop error, added sync/async compatibility.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional


class IA_Hoteles_MCP_Client:
    """Cliente para interactuar con el servidor MCP de IA Hoteles.
    
    Supports both async and sync usage. The sync methods use
    nested-event-loop-safe execution to avoid RuntimeError when
    called from an already-running event loop.
    """
    
    def __init__(self, server_script: str = "server_mcp.py"):
        self.server_script = server_script
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Llama a una herramienta del servidor MCP de forma asincrona.
        
        Args:
            tool_name: Name of the MCP tool to call.
            arguments: Arguments dictionary for the tool.
            
        Returns:
            Tool result dictionary.
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            raise ImportError(
                "MCP client requires the 'mcp' package. Install with: "
                "pip install mcp"
            )
        
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result
        except Exception as e:
            raise ConnectionError(f"MCP Tool Call Error: {e}") from e

    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Version sincrona con nested-loop-safe execution.
        
        Uses nest_asyncio if available, or runs in a separate thread
        if called from within an existing event loop.
        
        Args:
            tool_name: Name of the MCP tool to call.
            arguments: Arguments dictionary for the tool.
            
        Returns:
            Tool result dictionary.
        """
        try:
            loop = asyncio.get_running_loop()
            # We're inside a running event loop -- use nest_asyncio or thread
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(self.call_tool(tool_name, arguments))
            except ImportError:
                # Fallback: run in a new thread with its own event loop
                import concurrent.futures
                import threading
                
                result_container = {"value": None, "exception": None}
                
                def _run_in_thread():
                    try:
                        # Create a new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result_container["value"] = loop.run_until_complete(
                            self.call_tool(tool_name, arguments)
                        )
                    except Exception as e:
                        result_container["exception"] = e
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=_run_in_thread)
                thread.start()
                thread.join(timeout=60)
                
                if thread.is_alive():
                    raise TimeoutError("MCP tool call timed out after 60s")
                
                if result_container["exception"]:
                    raise result_container["exception"]
                
                return result_container["value"]
        except RuntimeError:
            # No running event loop -- safe to use asyncio.run()
            return asyncio.run(self.call_tool(tool_name, arguments))

    async def read_resource(self, uri: str) -> str:
        """Lee un recurso del servidor MCP.
        
        Args:
            uri: Resource URI to read.
            
        Returns:
            Resource content as string.
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            raise ImportError(
                "MCP client requires the 'mcp' package. Install with: "
                "pip install mcp"
            )
        
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    resource = await session.read_resource(uri)
                    if hasattr(resource, 'content') and resource.content:
                        return resource.content[0].text
                    return str(resource)
        except Exception as e:
            raise ConnectionError(f"MCP Resource Read Error: {e}") from e

    def read_resource_sync(self, uri: str) -> str:
        """Version sincrona de read_resource con nested-loop-safe execution."""
        try:
            loop = asyncio.get_running_loop()
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(self.read_resource(uri))
            except ImportError:
                import concurrent.futures
                import threading
                
                result_container = {"value": None, "exception": None}
                
                def _run_in_thread():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result_container["value"] = loop.run_until_complete(
                            self.read_resource(uri)
                        )
                    except Exception as e:
                        result_container["exception"] = e
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=_run_in_thread)
                thread.start()
                thread.join(timeout=60)
                
                if thread.is_alive():
                    raise TimeoutError("MCP resource read timed out after 60s")
                
                if result_container["exception"]:
                    raise result_container["exception"]
                
                return result_container["value"]
        except RuntimeError:
            return asyncio.run(self.read_resource(uri))

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Lista todas las herramientas disponibles en el servidor MCP.
        
        Returns:
            List of tool definitions.
        """
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script],
            env=None
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    tools = []
                    if hasattr(tools_result, 'tools'):
                        for tool in tools_result.tools:
                            tools.append({
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                            })
                    return tools
        except Exception as e:
            raise ConnectionError(f"MCP List Tools Error: {e}") from e

    def list_tools_sync(self) -> List[Dict[str, Any]]:
        """Version sincrona de list_tools."""
        try:
            asyncio.get_running_loop()
            try:
                import nest_asyncio
                nest_asyncio.apply()
                return asyncio.run(self.list_tools())
            except ImportError:
                import threading
                result_container = {"value": None, "exception": None}
                
                def _run_in_thread():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result_container["value"] = loop.run_until_complete(
                            self.list_tools()
                        )
                    except Exception as e:
                        result_container["exception"] = e
                    finally:
                        loop.close()
                
                thread = threading.Thread(target=_run_in_thread)
                thread.start()
                thread.join(timeout=30)
                if result_container["exception"]:
                    raise result_container["exception"]
                return result_container["value"] or []
        except RuntimeError:
            return asyncio.run(self.list_tools())
