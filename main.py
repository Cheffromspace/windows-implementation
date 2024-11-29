import asyncio
from mcp_handler import server

async def handle_client(reader, writer):
    await server.run(
        read_stream=reader,
        write_stream=writer,
        initialization_options={}
    )

async def main():
    # Start TCP server
    port = 8000
    srv = await asyncio.start_server(
        handle_client,
        '127.0.0.1',
        port
    )
    
    print(f"MCP server listening on port {port}")
    
    async with srv:
        await srv.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
