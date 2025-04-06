# generative-saleman

`generative-salesman` is an agentic Large Language Model (LLM) designed to act as a salesman for a board game sales platform. This project leverages an LLM to assist users with product-related queries and promote sales, utilizing a Modular Control Plane (MCP) as its tools management system.

## Project Overview

The goal of this project is to create an intelligent, conversational salesman powered by an LLM that can:
- Answer questions about board game products using provided tools.
- Upsell or promote products to users.
- Handle unsupported queries gracefully by directing users to the support team.

The MCP framework is used to manage and integrate various tools, which are implemented as servers in the `src/generative-saleman/server/` directory.

## Configuration

To enable tools, users must specify the `mcp_servers` section in the configuration file (e.g., `config.yaml`). Below is an example configuration:

```yaml
openai_config:
  openai_api_key: ""
  model_name: "gpt-4o-mini-2024-07-18"
  base_url: "https://api.openai.com/v1"

mcp_servers:
  product-info:
    command: "python"
    args: ["./src/generative-saleman/server/product_info.py"]

system_prompt: |
    You are a helpful assistant that can answer questions about product information using the tools provided to you.
    For critical questions where tools are not available, please respond with:
    "Please contact the support team for more information." Then, promote the product to the user. You can ask the user for more details about the product if needed.

```

### Configuration Details
- `openai_config`: Contains the API key, model name, and base URL for the OpenAI API integration.
- `mcp_servers`: Defines the tools (servers) available to the LLM. Each tool must specify a command and args to launch the server.
- `system_prompt`: The prompt that guides the LLM's behavior as a salesman.

## Tools Management (MCP Servers)

All tools are implemented as MCP servers and must reside in the `src/generative-saleman/server/` folder. For example:

- `product_info.py`: A server that provides product details for the LLM to use.

To add a new tool:

- Create a new Python script in `src/generative-saleman/server/`.
- Implement the server logic to handle requests and return relevant data.
- Update the `mcp_servers` section in the config file with the new tool's command and arguments.
