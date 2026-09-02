# MCP 서버, 초보자를 위한 정리

> 기준 문서: [modelcontextprotocol.io](https://modelcontextprotocol.io) 공식 문서
> (Architecture overview / Getting started intro), 프로토콜 버전 `2026-07-28`

---

## 1. 한 줄 요약

MCP(Model Context Protocol)는 **AI 애플리케이션을 외부 시스템에 연결하기 위한 오픈 표준**입니다.

공식 문서는 이걸 **"AI 애플리케이션용 USB-C 포트"**에 비유합니다. USB-C가 키보드든 모니터든 하나의 규격으로 꽂히게 해주듯, MCP는 파일 시스템·DB·검색엔진·외부 API를 하나의 규격으로 AI에 꽂아줍니다.

중요한 점 하나:

> MCP는 **"컨텍스트를 주고받는 규격"**만 정의합니다.
> AI가 그 컨텍스트로 무엇을 하는지, 어떤 LLM을 쓰는지는 MCP의 관심사가 아닙니다.

---

## 2. 슬라이드 그림 해석 — "MCP 서버는 대개 내 컴퓨터에서 돈다"

첨부한 슬라이드가 말하는 핵심은 이겁니다.

**"서버"라는 단어 때문에 클라우드를 떠올리기 쉽지만, MCP 서버는 대부분 내 노트북 안에서 도는 그냥 프로세스다.**

그림을 구조로 풀면:

```
[ 내 컴퓨터 ]
┌─────────────────────────────┐
│  Host (예: Claude Desktop)  │
│  ┌────────┐┌────────┐┌────────┐
│  │Client 1││Client 2││Client 3│
│  └───┬────┘└───┬────┘└───┬────┘
└──────│─────────│─────────│──────┘
       │         │         │
   ┌───▼───┐ ┌───▼───┐     │  ← 여기 두 개는 내 PC에서 실행
   │Server │ │Server │     │     (stdio 방식)
   └───────┘ └───┬───┘     │
                 │         └──────────► [ 원격 Server ]  ← HTTP 방식
                 │
                 └──► [ 외부 API ]  ← 서버가 대신 호출해줌
```

정리하면:

- MCP 서버는 **로컬에서도 원격에서도** 돌 수 있습니다. "서버"는 위치가 아니라 **역할**의 이름입니다.
- 로컬 서버는 보통 `stdio`(표준 입출력)로 붙습니다. 네트워크를 안 타므로 빠릅니다.
- 원격 서버는 `Streamable HTTP`로 붙습니다. 인증(OAuth 등)이 필요합니다.
- 로컬 stdio 서버는 보통 **클라이언트 하나만** 상대합니다. 원격 HTTP 서버는 **여러 클라이언트를 동시에** 상대합니다.
- 슬라이드 오른쪽 아래처럼, MCP 서버가 **외부 API를 대신 호출하는 껍데기** 역할만 하는 경우도 아주 흔합니다. 공식 예제 서버 상당수가 이 형태입니다.

---

## 3. 등장인물 3명

| 이름 | 정체 | 예시 |
|---|---|---|
| **Host** | MCP 클라이언트들을 관리하는 AI 애플리케이션 본체 | Claude Desktop, Claude Code, VS Code, Cursor |
| **Client** | 서버 **하나**와 연결을 유지하는 커넥터 | Host가 서버 개수만큼 내부에서 자동 생성 |
| **Server** | 실제로 도구·데이터를 제공하는 프로그램 | filesystem 서버, DB 서버, Sentry 서버 |

핵심 규칙: **클라이언트와 서버는 1:1**입니다.

VS Code가 Sentry 서버에 붙으면 클라이언트 객체 1개가 생기고, 이어서 filesystem 서버에도 붙으면 클라이언트 객체가 하나 더 생깁니다. Host는 여러 클라이언트를 동시에 들고 있습니다.

초보자가 가장 많이 헷갈리는 부분: **"클라이언트"는 내가 설치하거나 코딩하는 게 아닙니다.** Host가 알아서 만듭니다. 우리가 손대는 건 대부분 **서버**와 **설정 파일**뿐입니다.

---

## 4. 서버가 제공할 수 있는 것 (Primitives)

MCP 서버가 클라이언트에게 내놓을 수 있는 건 딱 세 종류입니다.

| 종류 | 뜻 | 누가 주도하나 | 예시 |
|---|---|---|---|
| **Tools** | AI가 호출해서 **실행**하는 함수 | 모델이 판단해서 호출 | `send_email`, `run_query`, 파일 쓰기 |
| **Resources** | AI에게 넣어줄 **읽기용 데이터** | 애플리케이션이 골라서 넣음 | 파일 내용, DB 스키마, API 응답 |
| **Prompts** | 재사용 가능한 **프롬프트 템플릿** | 보통 사용자가 선택 | 슬래시 명령어, few-shot 예시 |

각 종류마다 `*/list`(목록 조회), `*/get`(가져오기), 그리고 도구는 `tools/call`(실행) 메서드가 있습니다.

반대로 **클라이언트가 서버에게 제공하는 것**도 있습니다.

- **Elicitation**: 서버가 사용자에게 추가 정보를 되묻거나 확인을 요청하는 기능 (`elicitation/create`)

> 참고 — `2026-07-28` 버전에서 **Sampling과 Logging은 deprecated** 되었습니다.
> Sampling은 서버가 클라이언트의 LLM을 빌려 쓰는 기능이었는데, 이제 새 구현은 LLM 제공자 API를 직접 쓰라고 권장합니다. Logging은 `stderr`나 OpenTelemetry를 쓰라고 안내합니다.
> **2025년에 작성된 블로그·강의 대부분이 이 두 기능을 여전히 핵심으로 소개하고 있으니 주의하세요.**

---

## 5. 두 개의 층 (Layer)

MCP는 두 겹으로 되어 있습니다.

**① 데이터 계층 (안쪽)**
- **JSON-RPC 2.0** 기반의 메시지 규격
- 무엇을 주고받을지(도구/리소스/프롬프트/알림)를 정의
- 전송 방식이 뭐든 메시지 포맷은 동일

**② 전송 계층 (바깥쪽)**
- `stdio`: 같은 머신 안 프로세스끼리 표준 입출력으로 통신. 네트워크 오버헤드 없음
- `Streamable HTTP`: HTTP POST로 요청, 필요 시 SSE로 스트리밍. Bearer 토큰·API 키·커스텀 헤더 지원하며 **공식 문서는 OAuth 사용을 권장**

이 분리 덕분에 "서버 코드는 그대로 두고 전송 방식만 바꾸는" 일이 가능합니다.

---

## 6. 실제 동작 흐름 — 슬라이드의 "1. List Tools 2. Call Tool"

슬라이드 하단에 적힌 두 단계가 사실상 MCP의 전부입니다.

### 0단계: Discovery (선택)

클라이언트가 `server/discover`를 보내 서버의 버전·능력·신원을 한 번에 확인합니다. 모든 서버가 **반드시 구현해야 하는** 요청이지만, 클라이언트가 **보낼 의무는 없습니다.**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "server/discover",
  "params": {
    "_meta": {
      "io.modelcontextprotocol/protocolVersion": "2026-07-28",
      "io.modelcontextprotocol/clientInfo": { "name": "example-client", "version": "1.0.0" },
      "io.modelcontextprotocol/clientCapabilities": { "elicitation": {} }
    }
  }
}
```

### 1단계: List Tools

`tools/list`로 "너 뭐 할 수 있어?"를 물어봅니다. 응답에는 도구마다 이런 정보가 들어옵니다.

- `name`: 고유 식별자 (`calculate`보다 `calculator_arithmetic`처럼 명확하게 짓기를 권장)
- `title`: 사람에게 보여줄 이름
- `description`: 무엇을 하는 도구이고 언제 쓰는지
- `inputSchema`: JSON Schema로 정의된 입력 파라미터

Host는 연결된 모든 서버의 도구를 모아 하나의 목록으로 만들고, 그걸 LLM에게 보여줍니다.

### 2단계: Call Tool

LLM이 "이 도구를 써야겠다"고 판단하면 `tools/call`이 나갑니다.

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": { "location": "San Francisco", "units": "imperial" },
    "_meta": { "...": "매 요청마다 버전·능력·신원이 실림" }
  }
}
```

응답은 `content` 배열로 오며, 텍스트·이미지 등 여러 형식을 담을 수 있습니다. Host는 이 결과를 다시 대화에 넣어 LLM에게 돌려줍니다.

### 3단계: 알림 (선택)

도구 목록이 바뀌었을 때 서버가 알려주는 기능입니다. **opt-in**이라, 클라이언트가 `subscriptions/listen`으로 원하는 알림 종류를 명시해야 받습니다.

단, 공식 문서는 알림이 **best effort**라고 못 박습니다. 전송 재연결 과정에서 유실될 수 있으니 **폴링도 병행하라**고 권고합니다.

---

## 7. 초보자가 자주 하는 오해 5가지

**① "MCP 서버 = 클라우드 서버"**
→ 아닙니다. 대부분 내 컴퓨터에서 도는 프로세스입니다. 슬라이드의 주제이기도 합니다.

**② "MCP를 써야만 AI가 도구를 쓸 수 있다"**
→ 아닙니다. LLM의 function calling은 MCP 없이도 됩니다. MCP는 그걸 **여러 앱이 공유 가능한 표준 규격**으로 만든 것입니다.

**③ "MCP 서버를 만들면 AI가 알아서 잘 쓴다"**
→ 아닙니다. 도구의 `description`과 `inputSchema`가 곧 LLM에게 주는 설명서입니다. 이게 부실하면 모델이 엉뚱하게 씁니다.

**④ "MCP는 상태를 유지하는 세션 프로토콜이다"**
→ **버전에 따라 다릅니다.** `2026-07-28`부터 MCP는 **stateless(무상태)**로 바뀌었습니다. 모든 요청이 `_meta`에 프로토콜 버전과 능력 정보를 스스로 싣고 다니므로, 서버는 이전 요청을 기억할 필요가 없습니다. 로드밸런서 뒤 아무 인스턴스에나 요청이 떨어져도 됩니다. **2025년 스펙(2025-03-26, 2025-06-18 등)은 stateful 세션 기반이었습니다.**

**⑤ "설치만 하면 안전하다"**
→ MCP Server가 내 컴퓨터에서 실행된다는 것은 데이터를 외부 서버에 보내지 않을 수도 있다는 장점이 있을 뿐, 설치 자체가 안전을 보장하지는 않습니다.로컬 프로그램도 위험한 작업을 할 수 있음

---



### 공식 링크

- 입문: https://modelcontextprotocol.io/docs/getting-started/intro
- 아키텍처: https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture
- 최신 스펙: https://modelcontextprotocol.io/specification/latest
- SDK 목록: https://modelcontextprotocol.io/docs/2026-07-28/sdk
- 레퍼런스 서버: https://github.com/modelcontextprotocol/servers
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- 문서 전체 색인: https://modelcontextprotocol.io/llms.txt
