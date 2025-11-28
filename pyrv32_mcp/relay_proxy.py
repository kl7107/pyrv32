#!/usr/bin/env python3
"""
Dumb byte relay between VS Code (stdio) and MCP TCP server.

This proxy doesn't understand MCP protocol at all - it just forwards
bytes bidirectionally between stdin/stdout and a TCP connection.

VS Code <--stdio--> Relay Proxy <--TCP--> MCP Sim Server
"""

import asyncio
import sys


async def relay_stdio_to_tcp(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Forward data from stdin to TCP connection."""
    stdin_reader = asyncio.StreamReader()
    await asyncio.get_event_loop().connect_read_pipe(
        lambda: asyncio.StreamReaderProtocol(stdin_reader),
        sys.stdin.buffer
    )
    
    try:
        while True:
            data = await stdin_reader.read(4096)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except Exception as e:
        print(f"stdio->tcp error: {e}", file=sys.stderr)
    finally:
        writer.close()
        await writer.wait_closed()


async def relay_tcp_to_stdio(reader: asyncio.StreamReader):
    """Forward data from TCP connection to stdout."""
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    except Exception as e:
        print(f"tcp->stdio error: {e}", file=sys.stderr)


async def main():
    """Connect to TCP server and relay bytes bidirectionally."""
    host = "127.0.0.1"
    port = 5555
    
    try:
        # Connect to the MCP simulator server
        reader, writer = await asyncio.open_connection(host, port)
        
        # Start bidirectional relay
        await asyncio.gather(
            relay_stdio_to_tcp(reader, writer),
            relay_tcp_to_stdio(reader)
        )
    except Exception as e:
        print(f"Relay error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
