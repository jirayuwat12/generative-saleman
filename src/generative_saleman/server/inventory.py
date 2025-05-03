import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import Client, create_client

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

# Initialize Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Create a FastMCP object
mcp = FastMCP(
    name="generative-saleman-product-info",
    dependencies=["supabase", "dotenv"],
    description="A tool to get product price.",
    version="0.0.1",
)

@mcp.tool()
def get_product_amount(product_name: str) -> int | None:
    """
    Get the amount of the given product name and the function will return None if there is no such product in the database.

    :param product_name: The name of the product.
    :type product_name: str

    :return: The amount of the product.
    :rtype: int
    """
    # Query the amount from the database
    response = supabase.table("products")\
        .select("amount")\
        .eq("name", product_name)\
        .execute()
    if response.data:
        return response.data[0]["amount"]
    else:
        return None
