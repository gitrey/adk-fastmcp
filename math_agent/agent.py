# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os

import google.auth
import google.oauth2.id_token
import google.auth.transport.requests

from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


async def get_sum(a: int, b: int) -> int:
    """Get sum for two numbers

    Args:
        a: number
        b: number

    Returns:
        the sum of two numbers.
    """
    common_exit_stack = AsyncExitStack()

    mcp_tool_url = "https://fastmcp-demo-00000000000.us-central1.run.app"
    request = google.auth.transport.requests.Request()
    target_audience = mcp_tool_url

    # For an agent running on GCP runtimes, consider using:
    # https://cloud.google.com/docs/authentication/get-id-token#metadata-server
    # This can be used at global scope of agent, and then use the .refresh() method
    # on the credential which will only call metadata service once per hour
    id_token = google.oauth2.id_token.fetch_id_token(request, target_audience)

    tools, _ = await MCPToolset.from_server(
        connection_params=SseServerParams(
            url="https://fastmcp-demo-00000000000.us-central1.run.app/sse",
            headers={"Authorization": f"Bearer {id_token}"},
        ),
        async_exit_stack=common_exit_stack
    )

    return await tools[0].run_async(
        args={
            "a": a,
            "b": b,
        },
        tool_context=None,
    )


root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    instruction="You are a helpful AI assistant designed to provide accurate and useful information.",
    tools=[get_sum],
)
