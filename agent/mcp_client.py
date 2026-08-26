import sys
from pathlib import Path
from typing import Any

from langchain_mcp_adapters.client import MultiServerMCPClient


PROJECT_ROOT=Path(__file__).resolve().parent.parent


def create_mcp_client()->MultiServerMCPClient:
	"""
	Event MCP 서버에 연결하는 client를 생성합니다.
	"""
	return MultiServerMCPClient(
		{
			"event_server": {
				"transport": "stdio",
				"command": sys.executable,
				"args": ["-m", "mcp.event_mcp"],
				"cwd": str(PROJECT_ROOT), # MCP 서버 프로세스의 작업 디렉터리를 프로젝트 루트로 지정
			}
		}
	)


async def get_event_mcp_tools()->list[Any]:
	"""
	Event MCP 서버에 등록된 도구 목록을 반환합니다.
	"""
	client=create_mcp_client()
	return await client.get_tools()
