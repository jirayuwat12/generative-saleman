import argparse
import asyncio

import nest_asyncio
import streamlit as st
import yaml

# Import message class from langchain
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from generative_saleman.utils.llm_chat import generate_chat

# Allow nested asyncio loops
nest_asyncio.apply()

# Load the configuration file
argparser = argparse.ArgumentParser(description="Load configuration file.")
argparser.add_argument(
    "-C", "--config", type=str, default="./configs/chatbot_streamlit.yaml", help="Path to the configuration file"
)
argparser.add_argument("-D", "--debug", action="store_true", help="Enable debug mode")

args = argparser.parse_args()
with open(args.config, "r") as f:
    config_yaml = yaml.safe_load(f)
    openai_config = config_yaml["openai_config"]

# Create the language model
model = ChatOpenAI(
    model=openai_config["model_name"],
    api_key=openai_config["openai_api_key"],
)

# Set the title of the Streamlit app
st.title(config_yaml["streamlit_title"])

# Initialize messages in the session state if not already present
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage(config_yaml["system_prompt"]),
        AIMessage(config_yaml["welcome_message"]),
    ]

# Display previous chat messages in the app
instance_to_role_name = {
    HumanMessage: "user",
    AIMessage: "assistant",
    SystemMessage: "system",
}
for msg in st.session_state["messages"]:
    for msg_type, role_name in instance_to_role_name.items():
        if isinstance(msg, msg_type):
            st.chat_message(role_name).markdown(msg.content)
            break
    else:
        st.chat_message("unknown").markdown(msg.content)

# Check if user inputs a message in the chat input field
if prompt := st.chat_input(placeholder=config_yaml["streamlit_input_placeholder"]):
    # Add user's message to the session state messages
    st.session_state["messages"].append(HumanMessage(prompt))
    st.chat_message("user").write(prompt)  # Display user's message in the chat

    with st.chat_message("assistant"):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            generate_chat(model, config_yaml["mcp_servers"], st.session_state["messages"])
        )
        st.session_state["messages"] = response
        if args.debug:
            print("-" * 50, "DEBUG MODE", "-" * 50)
            print(f"Message length: {len(st.session_state['messages'])}")
            print(f"Last message  : {st.session_state['messages'][-1].content}")
            print("-" * 112)
        st.write(response[-1].content)
