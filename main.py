#/usr/bin/python

import sys
import asyncio
from asyncio import StreamReader, StreamWriter
from typing import NamedTuple, TypedDict

params = {
    "host": "127.0.0.1",
    "port": "8080"
}

class Headers(TypedDict):
    name: str
    value: str

class RequestData(NamedTuple):
    method: str
    uri: str
    protocol: str
    headers: Headers

    def get_log(self):
        return f"{self.method} {self.uri}"

async def read_headers(reader: StreamReader) -> Headers:
    headers = Headers()
    
    while True:
        header_bytes = await reader.readline()
        if header_bytes == b'\r\n':
            break
        else:
            header_text = header_bytes.decode("utf-8").rstrip()
            name, value = header_text.split(": ")
            headers[name] = value
    
    return headers

async def write_response(request_data: RequestData, writer: StreamWriter):
    if (request_data.uri != "/"):
        writer.write("HTTP/1.0 404 NA\r\n".encode())
        writer.write("Content-Type: text/plain\r\n".encode())
        writer.write("\r\n".encode())
        writer.write("Not found".encode())
    else:
        writer.write("HTTP/1.0 200 NA\r\n".encode())
        writer.write("Content-Type: application/json\r\n".encode())
        writer.write("\r\n".encode())
        writer.write(f'{{"uri": "{request_data.uri}", "method": "{request_data.method}"}}\r\n'.encode())
    await writer.drain()

async def handle(reader: StreamReader, writer: StreamWriter):
    try:
        request_line_bytes = await reader.readline()
        request_line = request_line_bytes.decode("ascii").rstrip()
        method, uri, protocol = request_line.split(' ')
        headers = await read_headers(reader)

        request_data = RequestData(method, uri, protocol, headers)

        print(request_data.get_log())

        await write_response(request_data, writer)
    except:
        pass
    finally:
        writer.close()

def main() -> int:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        server = asyncio.start_server(handle, host=params["host"], port=params["port"])
        loop.create_task(server)
        loop.run_forever()
        return 0
    except:
        return 1
    finally:
        if loop is None:
            loop.close()

if __name__ == "__main__":
    code = main()
    sys.exit(code)

