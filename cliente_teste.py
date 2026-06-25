# cliente_teste.py
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _payload(resultado):
    """Extrai o dado da tool, tolerando variacoes entre versoes do SDK MCP."""
    # SDKs recentes expoem o objeto ja desserializado em structuredContent.
    structured = getattr(resultado, "structuredContent", None)
    if isinstance(structured, dict):
        # FastMCP embrulha retornos de lista em {"result": [...]}.
        if set(structured.keys()) == {"result"}:
            return structured["result"]
        return structured
    # Fallback: o conteudo textual carrega o JSON serializado.
    return json.loads(resultado.content[0].text)


async def main() -> dict:
    params = StdioServerParameters(command="python", args=["servidor_mcp.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            nomes = [t.name for t in tools.tools]

            criar = await session.call_tool("criar_tarefa", {"titulo": "tarefa via mcp"})
            listar = await session.call_tool("listar_tarefas", {})

            return {
                "tools": nomes,
                "criar_resultado": _payload(criar),
                "listar_resultado": _payload(listar),
            }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main())))
