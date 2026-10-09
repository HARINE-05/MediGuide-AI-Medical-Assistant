import asyncio
import json
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_many(requests: list[tuple[str, dict]]) -> list[dict]:
    server = Path(__file__).resolve().parents[1] / 'mcp_server.py'
    params = StdioServerParameters(command=sys.executable, args=[str(server)])
    async with asyncio.timeout(35):
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                answers = []
                for name, arguments in requests:
                    result = await session.call_tool(name, arguments)
                    if result.isError:
                        raise RuntimeError('MCP tool failed')
                    structured = getattr(result, 'structuredContent', None)
                    if structured is not None:
                        answers.append(structured)
                    else:
                        payload = '\n'.join(c.text for c in result.content if hasattr(c, 'text'))
                        answers.append(json.loads(payload))
                return answers

def call(name: str, args: dict) -> dict:
    return asyncio.run(call_many([(name, args)]))[0]
