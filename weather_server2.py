# weather_server2.py
# MCP 서버 라이브러리에서 FastMCP 클래스를 가져옴
from mcp.server.fastmcp import FastMCP

# "Weather"라는 이름의 MCP 서버 인스턴스를 생성 (stdio 방식이므로 port 인자를 제거)
mcp = FastMCP("Weather")


# 이 함수를 MCP 도구(tool)로 등록하는 데코레이터
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""  # 지정한 위치의 날씨를 조회하는 도구 (docstring은 클라이언트에 도구 설명으로 전달됨)
    # 고정된 날씨 문자열을 반환 (실제 API 호출 없이 테스트용 응답)
    return "It's always sunny in New York"


# 이 파일이 직접 실행될 때만 아래 코드를 실행
if __name__ == "__main__":
    # stdio 전송 방식으로 MCP 서버를 실행 (표준입출력으로 클라이언트와 통신)
    # stdout은 JSON-RPC 통신 채널로 사용되므로 print() 출력을 넣지 않음
    mcp.run(transport="stdio")