import unittest
from langchain_openai import ChatOpenAI
import yaml
from langchain_core.messages import HumanMessage, ToolMessage
from generative_saleman.utils.llm_chat import generate_chat
import asyncio
from collections import defaultdict
import warnings
from .calculator_testcases import ADDITION_TEST_CASES, SUBSTRACTION_TEST_CASES, MULTIPLICATION_TEST_CASES, COMPLEX_TEST_CASES

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.config_yaml = yaml.safe_load(open("./tests/tools/calculator_config.yaml", "r"))
        self.mcp_config = self.config_yaml["mcp_servers"]
        self.model = ChatOpenAI(
            model = self.config_yaml["openai_config"]["model_name"],
            api_key = self.config_yaml["openai_config"]["openai_api_key"],
        )

    def test_addition_calculator(self):
        # Define the prompt for the calculator
        for test_case in ADDITION_TEST_CASES:
            promt = HumanMessage(
                content=test_case["human_input"],
            )

            # Generate a response using the model
            response = asyncio.run(generate_chat(self.model, self.mcp_config, promt))

            tool_called = False
            for msg in response:
                if isinstance(msg, ToolMessage):
                    self.assertEqual(tool_called, False) # Ensure the tool is called only once
                    self.assertEqual(msg.name, test_case["tool_name"])
                    self.assertEqual(msg.content, test_case["content"])
                    tool_called = True
            self.assertEqual(tool_called, True) # Ensure the tool was called

    def test_subtraction_calculator(self):
        # Define the prompt for the calculator
        for test_case in SUBSTRACTION_TEST_CASES:
            promt = HumanMessage(
                content=test_case["human_input"],
            )

            # Generate a response using the model
            response = asyncio.run(generate_chat(self.model, self.mcp_config, promt))

            tool_called = False
            for msg in response:
                if isinstance(msg, ToolMessage):
                    self.assertEqual(tool_called, False)
                    self.assertEqual(msg.name, test_case["tool_name"])
                    self.assertEqual(msg.content, test_case["content"])
                    tool_called = True
            self.assertEqual(tool_called, True)

    def test_multiplication_calculator(self):
        # Define the prompt for the calculator
        for test_case in MULTIPLICATION_TEST_CASES:
            promt = HumanMessage(
                content=test_case["human_input"],
            )

            # Generate a response using the model
            response = asyncio.run(generate_chat(self.model, self.mcp_config, promt))

            tool_called = False
            for msg in response:
                if isinstance(msg, ToolMessage):
                    self.assertEqual(tool_called, False)
                    self.assertEqual(msg.name, test_case["tool_name"])
                    self.assertEqual(msg.content, test_case["content"])
                    tool_called = True
            self.assertEqual(tool_called, True)

    def test_complex_calculator(self):
        # Define the prompt for the calculator
        for test_case in COMPLEX_TEST_CASES:
            promt = HumanMessage(
                content=test_case["human_input"],
            )

            # Generate a response using the model
            response = asyncio.run(generate_chat(self.model, self.mcp_config, promt))

            tool_called = defaultdict(bool)
            for msg in response:
                if isinstance(msg, ToolMessage):
                    self.assertIn(msg.name, test_case["tool_names"])
                    tool_called[msg.name] = True
            if len(tool_called.keys()) == 0:
                self.assertEqual(tool_called, False)
