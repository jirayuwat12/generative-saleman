import asyncio
import os
import yaml
import argparse
import nest_asyncio
import streamlit as st
from mcp_openai import MCPClient, config

nest_asyncio.apply()

# Load the configuration file
argparser = argparse.ArgumentParser(description="Load configuration file.")
argparser.add_argument(
    "-c", "--config", type=str, default="./configs/chatbot_streamlit.yaml", help="Path to the configuration file"
)
args = argparser.parse_args()
with open(args.config, "r") as f:
    config_yaml = yaml.safe_load(f)
    openai_config = config_yaml["openai_config"]

# Set OpenAI API key from environment variable
os.environ["OPENAI_API_KEY"] = openai_config["openai_api_key"]

# Set the title of the Streamlit app
st.title("💰 Generative Saleman.")

# Set the MCP Server and Client configurations
mcp_client_config = config.MCPClientConfig(
    mcpServers={
        server_name: config.MCPServerConfig(
            command=server_config["command"],
            args=server_config["args"],
        )
        for server_name, server_config in config_yaml["mcp_servers"].items()
    }
)
llm_climent_config = config.LLMClientConfig(
    api_key=openai_config["openai_api_key"],
    base_url=openai_config["base_url"],
)
llm_request_config = config.LLMRequestConfig(
    model=openai_config["model_name"],
)
client = MCPClient(
    mpc_client_config=mcp_client_config,
    llm_client_config=llm_climent_config,
    llm_request_config=llm_request_config,
)

# [ ]: Test for multiple servers
# Connect to the MCP server
try:
    loop = asyncio.get_event_loop()
except RuntimeError as e:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
for server_name, server_config in config_yaml["mcp_servers"].items():
    print(f"Connecting to {server_name}...")
    loop.run_until_complete(client.connect_to_server(server_name))

# Initialize messages in the session state if not already present
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": config_yaml["system_prompt"],
        },
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can help you purchase products. Please ask me about the price of a product.",
        },
    ]

# Display previous chat messages in the app
for msg in st.session_state.messages:
    if "content" not in msg or msg["role"] == "system":
        continue
    st.chat_message(msg["role"]).write(msg["content"])

# Check if user inputs a message in the chat input field
if prompt := st.chat_input(placeholder="What's the price of the product?"):
    # Add user's message to the session state messages
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)  # Display user's message in the chat

    with st.chat_message("assistant"):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            client.process_messages(
                messages=st.session_state.messages,
            )
        )
        st.session_state.messages = response
        st.write(response[-1]["content"])
