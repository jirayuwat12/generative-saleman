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
            st.chat_message(role_name).markdown(msg.content)
            break
    # else:
    # st.chat_message("unknown").markdown(msg.content)

# Toggle mode
input_mode = st.toggle("📝 สลับระหว่างพิมพ์ข้อความ / แนบรูปภาพ", value=True)  # True = ข้อความ, False = รูป

if input_mode:
    # โหมดข้อความ
    prompt = st.chat_input(placeholder=config_yaml["streamlit_input_placeholder"])
    if prompt:
        st.session_state["messages"].append(HumanMessage(prompt))
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                generate_chat(model, config_yaml["mcp_servers"], st.session_state["messages"])
            )
            st.session_state["messages"] = response
            st.write(response[-1].content)
else:
    # โหมดรูปภาพ
    uploaded_file = st.file_uploader("📷 แนบรูปภาพสลิป (png, jpg, jpeg)", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        file_bytes = uploaded_file.read()

        # 🔐 สร้าง path สำหรับเซฟรูป
        upload_dir = "./uploaded_slips"
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = uploaded_file.name.split(".")[-1]
        file_name = f"slip_{uuid.uuid4().hex}.{file_ext}"
        file_path = os.path.join(upload_dir, file_name)

        # 💾 เซฟรูปลงเครื่อง
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # แสดงในแชท
        st.chat_message("user").image(file_bytes, width=300)

        # 📨 ส่ง path เข้า LLM
        st.session_state["messages"].append(HumanMessage(f"จ่ายเงินด้วยไฟล์ภาพ: <image_path>{file_path}</image_path>"))

        with st.chat_message("assistant"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                generate_chat(model, config_yaml["mcp_servers"], st.session_state["messages"])
            )
            st.session_state["messages"] = response
            st.write(response[-1].content)
