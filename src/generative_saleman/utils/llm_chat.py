from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent


async def generate_chat(
    llm_model: BaseChatModel, mcp_servers_config: dict[str, dict[str, str]], messages: list[BaseMessage]
) -> list[BaseMessage]:
    """
    Generate chat responses based on user messages.

    :param llm_model: The language model to use for generating responses.
    :type llm_model: BaseChatModel
    :param mcp_servers_config: The configuration for the MCP servers.
    :type mcp_servers_config: dict[str, dict[str, str]] which "name" is the key and "command", "args", "transform" are the dictionary values.
    :param messages: The list of messages to process.
    :type messages: list[BaseMessage]

    :return: The response from the agent.
    :rtype: list[BaseMessage]
    """
    async with MultiServerMCPClient(mcp_servers_config) as client:
        agent = create_react_agent(llm_model, client.get_tools())
        response = await agent.ainvoke(
            {
                "messages": messages,
            }
        )
        return response["messages"]
