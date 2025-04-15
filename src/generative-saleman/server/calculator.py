from mcp.server.fastmcp import FastMCP


# Create a FastMCP object
mcp = FastMCP(
    name="generative-saleman-calculator",
    description="A tool to make LLM work with numeric calculations and math more efficiently, and to help LLMs with math problems.",
    version="0.0.1",
)


@mcp.tool(name="Addition", description="Add two numbers")
def add_numbers(a: float, b: float, precision: int = 4) -> float:
    """
    Add two numbers together.
    
    Args:
        a (float): The first number.
        b (float): The second number.
        precision (int): The number of decimal places to round the result to. Default is 4.

    Returns:
        float: The sum of the two numbers rounded to the specified precision.

    Example:
        >>> add_numbers(1.23456, 2.34567)
        3.5802
        >>> add_numbers(1.23456, 2.34567, precision=2)
        3.58
        >>> add_numbers(1.23456, 2.34567, precision=0)
        4
    """
    return round(a + b, precision)

@mcp.tool(name="Subtraction", description="Subtract two numbers")
def subtract_numbers(a: float, b: float, precision: int = 4) -> float:
    """
    Subtract two numbers.
    
    Args:
        a (float): The first number.
        b (float): The second number.
        precision (int): The number of decimal places to round the result to. Default is 4.

    Returns:
        float: The difference of the two numbers rounded to the specified precision.

    Example:
        >>> subtract_numbers(5.6789, 2.3456)
        3.3333
        >>> subtract_numbers(5.6789, 2.3456, precision=2)
        3.33
        >>> subtract_numbers(5.6789, 2.3456, precision=0)
        3
    """
    return round(a - b, precision)

@mcp.tool(name="Multiplication", description="Multiply two numbers")
def multiply_numbers(a: float, b: float, precision: int = 4) -> float:
    """
    Multiply two numbers.
    
    Args:
        a (float): The first number.
        b (float): The second number.
        precision (int): The number of decimal places to round the result to. Default is 4.

    Returns:
        float: The product of the two numbers rounded to the specified precision.

    Example:
        >>> multiply_numbers(1.1111, 2)
        2.2222
        >>> multiply_numbers(1.1111, 2, precision=2)
        2.22
        >>> multiply_numbers(1.1111, 2, precision=0)
        2
    """
    return round(a * b, precision)


if __name__ == "__main__":
    mcp.run()
