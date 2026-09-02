# weather_server.py
# 타입 힌트를 위한 List를 가져옴
from typing import List
# MCP 서버 라이브러리에서 FastMCP 클래스를 가져옴
from mcp.server.fastmcp import FastMCP

# "Weather"라는 이름의 MCP 서버 인스턴스를 생성하고, 서버 포트를 8001로 지정
mcp = FastMCP("Weather", port=8001)

# 이 함수를 MCP 도구(tool)로 등록하는 데코레이터
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""  # 지정한 위치의 날씨를 조회하는 도구 (docstring은 클라이언트에 도구 설명으로 전달됨)
    # 고정된 날씨 문자열을 반환 (실제 API 호출 없이 테스트용 응답)
    return "It's always sunny in New York"

# 이 파일이 직접 실행될 때만 아래 코드를 실행
if __name__ == "__main__":
    # http 전송 방식으로 MCP 서버를 실행 (포트 8001에서 대기)
    mcp.run(transport="streamable-http")