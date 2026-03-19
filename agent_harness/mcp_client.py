
import json
import asyncio
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class IA_Hoteles_MCP_Client:
    """
    Cliente para interactuar con el servidor MCP de IA Hoteles.
    """
    
    def __init__(self, server_script: str = "server_mcp.py"):
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_script],
            env=None
        )

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Llama a una herramienta del servidor MCP de forma asíncrona.
        """
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result
        except Exception as e:
            print(f"MCP Tool Call Error: {e}")
            raise

    def call_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Versión síncrona para compatibilidad con el pipeline actual.
        """
        return asyncio.run(self.call_tool(tool_name, arguments))

    async def read_resource(self, uri: str) -> str:
        """
        Lee un recurso del servidor MCP.
        """
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    resource = await session.read_resource(uri)
                    if hasattr(resource, 'content') and resource.content:
                        return resource.content[0].text
                    return str(resource)
        except Exception as e:
            print(f"MCP Resource Read Error: {e}")
            raise
