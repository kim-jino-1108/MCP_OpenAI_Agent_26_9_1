# math_server.py
# MCP 서버 라이브러리에서 FastMCP 클래스를 가져옴
from mcp.server.fastmcp import FastMCP

# "Math"라는 이름의 MCP 서버 인스턴스를 생성
mcp = FastMCP("Math")

# 이 함수를 MCP 도구(tool)로 등록하는 데코레이터
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""  # 두 숫자를 더하는 도구 (docstring은 클라이언트에 도구 설명으로 전달됨)
    # 두 정수 a와 b를 더한 결과를 반환
    return a + b

# 이 함수를 MCP 도구(tool)로 등록하는 데코레이터
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""  # 두 숫자를 곱하는 도구 (docstring은 클라이언트에 도구 설명으로 전달됨)
    # 두 정수 a와 b를 곱한 결과를 반환
    return a * b

# 이 파일이 직접 실행될 때만 아래 코드를 실행
if __name__ == "__main__":
    # 서버 시작 안내 메시지를 콘솔에 출력
    print("MCP server started and waiting for clients...")
    # streamable-http 전송 방식으로 MCP 서버를 실행 (기본적으로 http://localhost:8000/mcp 에서 대기)
    mcp.run(transport="streamable-http")