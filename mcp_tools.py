## Model Context Protocol Tools
# /**
#  *
#  * Model Context Protocol Tools
#  * Created by mychen76 in 2025-03.06
#  * Copyright (c) 2025. All rights reserved.
#  *
#  */
#

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_core.models import ModelFamily
from autogen_core import CancellationToken
from agents import function_tool
from pathlib import Path

## Ollama OpenAI Model
model_client = OpenAIChatCompletionClient(
    model="qwen2.5:14b",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": False,
        "family": ModelFamily.ANY,
    },
)

@function_tool(name_override="files_mcp_tool", description_override="Provides direct access to local file systems to read, write, and manage files within specified directories.")
async def files_mcp_tool(task:str, work_dir:str="./mcp_working") -> None:
    # Setup server params for local filesystem access
    path = Path(work_dir)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{work_dir}' created.")
    else:
        print(f"Directory '{work_dir}' already exists.")    
    allow_dirs=work_dir    
    server_params = StdioServerParams(
        command="npx", args=["-y", "@modelcontextprotocol/server-filesystem", allow_dirs]
    )
    # Get all available tools from the server
    tools = await mcp_server_tools(server_params)
    # Create an agent that can use all the tools
    agent = AssistantAgent(
        name="file_manager",
        model_client=model_client, 
        tools=tools, 
    )
    # The agent can now use any of the filesystem tools
    result = await agent.run(task=task, cancellation_token=CancellationToken())
    print(result.messages[-1].content)
    return result.messages[-1].content

@function_tool(name_override="webfetch_mcp_tool", description_override="fetch web url content and summarize it")
async def webfetch_mcp_tool(task:str) -> None:
    # Get the fetch tool from mcp-server-fetch.
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    tools = await mcp_server_tools(fetch_mcp_server)

    # Create an agent that can use the fetch tool.
    agent = AssistantAgent(name="fetcher", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore

    # Let the agent fetch the content of a URL and summarize it.
    result = await agent.run(task=f"{task}")    
    #result = await agent.run(task="Summarize the content of https://en.wikipedia.org/wiki/Seattle")
    print(result.messages[-1].content)
    return result.messages[-1].content

if __name__ == "__main__":
    # task="Summarize the content of https://www.aa.com/homePage.do?locale=en_CA"
    task="summarize the content of https://www.cntraveler.com/galleries/best-airlines-in-us and give me a recommend airline."
    asyncio.run(webfetch_mcp_tool(task))
    
    # task="list directory content in `./mcp_working`"    
    # task="write_file name `./mcp_working/mcptest.txt' with some content"
    # task="list files in directory name `./mcp_working`"    
    #asyncio.run(files_mcp_tool(task))
