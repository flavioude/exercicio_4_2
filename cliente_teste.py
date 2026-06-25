# cliente_teste.py
import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _como_objeto(resultado) -> dict:
    """Retorno de tool que e um objeto unico (ex.: criar_tarefa)."""
    structured = getattr(resultado, "structuredContent", None)
    if isinstance(structured, dict):
        # FastMCP embrulha retornos nao-dict em {"result": ...}.
        if set(structured.keys()) == {"result"}:
            return structured["result"]
        return structured
    return json.loads(resultado.content[0].text)


def _como_lista(resultado) -> list:
    """Retorno de tool que e uma lista (ex.: listar_tarefas).

    Em algumas versoes do SDK cada item da lista vira um content block
    separado, entao juntamos todos os blocks em uma unica lista.
    """
    structured = getattr(resultado, "structuredContent", None)
    if isinstance(structured, dict) and set(structured.keys()) == {"result"}:
        return structured["result"]
    return [json.loads(bloco.text) for bloco in resultado.content]


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
                "criar_resultado": _como_objeto(criar),
                "listar_resultado": _como_lista(listar),
            }


if __name__ == "__main__":
    print(json.dumps(asyncio.run(main())))
