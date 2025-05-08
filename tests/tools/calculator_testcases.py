ADDITION_TEST_CASES = [
    {
        "human_input": "2 + 2",
        "tool_name": "Addition",
        "content": "4.0"
    },
    {
        "human_input": "1.23456 + 2.34567",
        "tool_name": "Addition",
        "content": "3.5802"
    },
    {
        "human_input": "1.23456 + 2.34567, precision=2",
        "tool_name": "Addition",
        "content": "3.58"
    },
    {
        "human_input": "1.23456 + 2.34567, precision=0",
        "tool_name": "Addition",
        "content": "4"
    }
]

SUBSTRACTION_TEST_CASES = [
    {
        "human_input": "5.6789 - 2.3456",
        "tool_name": "Subtraction",
        "content": "3.3333"
    },
    {
        "human_input": "5.6789 - 2.3456 with the precision=2",
        "tool_name": "Subtraction",
        "content": "3.33"
    },
    {
        "human_input": "5.6789 - 2.3456 with the precision=0",
        "tool_name": "Subtraction",
        "content": "3"
    }
]

MULTIPLICATION_TEST_CASES = [
    {
        "human_input": "2 * 3",
        "tool_name": "Multiplication",
        "content": "6.0"
    },
    {
        "human_input": "1.23456 * 2.34567",
        "tool_name": "Multiplication",
        "content": "2.8959"
    },
    {
        "human_input": "1.23456 * 2.34567 with the precision=2",
        "tool_name": "Multiplication",
        "content": "2.9"
    },
    {
        "human_input": "1.23456 * 2.34567, precision=0",
        "tool_name": "Multiplication",
        "content": "3"
    }
]

COMPLEX_TEST_CASES = [
    {
        "human_input": "2 + 3 * 4 - 5",
        "tool_names": ["Addition", "Multiplication", "Subtraction"],
    },
    {
        "human_input": "(1 + 2) * (3 - 4)",
        "tool_names": ["Addition", "Multiplication", "Subtraction"],
    },
    {
        "human_input": "(1 + 2) * (3 + 4), precision=2",
        "tool_names": ["Addition", "Multiplication"],
    },
    {
        "human_input": "(1 + 2) * (3 - 4), precision=0",
        "tool_names": ["Addition", "Multiplication", "Subtraction"],
    }
]