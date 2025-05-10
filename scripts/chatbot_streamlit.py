import argparse
import asyncio
import base64
import os
import uuid

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
            if msg.content.strip() != "":
                st.chat_message(role_name).markdown(msg.content)
                break
    # else:
    # st.chat_message("unknown").markdown(msg.content)

# Toggle mode
uploaded_file = st.sidebar.file_uploader("แนบรูปภาพสลิป (png, jpg, jpeg)", type=["png", "jpg", "jpeg"])
prompt = st.chat_input(placeholder=config_yaml["streamlit_input_placeholder"])

if uploaded_file:
    # 💾 เซฟไฟล์ลงเครื่อง
    file_bytes = uploaded_file.read()
    upload_dir = "./uploaded_slips"
    os.makedirs(upload_dir, exist_ok=True)
    file_ext = uploaded_file.name.split(".")[-1]
    file_name = f"slip_{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(upload_dir, file_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # แสดงในแชท
    file_prompt = f"จ่ายเงินด้วยไฟล์ภาพ: {file_path}"
    st.session_state["messages"].append(AIMessage(file_prompt))
    st.chat_message("user").write(file_prompt)

if prompt:
    st.session_state["messages"].append(HumanMessage(prompt))
    st.chat_message("user").write(prompt)

if prompt or uploaded_file:
    with st.chat_message("assistant"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            generate_chat(model, config_yaml["mcp_servers"], st.session_state["messages"])
        )
        st.session_state["messages"] = response
        st.write(response[-1].content)
