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
def get_product_price(product_name: str) -> float | None:
    """
    Get the price of the given product name and the function will return None if the system is not selling the product.
    :param product_name: The name of the product.
    :type product_name: str

    :return: The price of the product.
    :rtype: float

    ## Example
    > get_product_price('apple')
    55.0
    > get_product_price('banana')
    5.0
    > get_product_price('no-product')
    None
    """
    # Query the product price from the database
    response = supabase.table("products").select("price").eq("name", product_name).execute()
    if response.data:
        return response.data[0]["price"]
    else:
        return None

@mcp.tool()
def is_selling_product(product_name: str) -> bool:
    """
    Check if the given product name is selling in the system.
    :param product_name: The name of the product.
    :type product_name: str

    :return: True if the product is selling, False otherwise.
    :rtype: bool

    ## Example
    > is_selling_product('apple')
    True
    > is_selling_product('banana')
    True
    > is_selling_product('no-product')
    False
    """
    # Query the product price from the database
    response = supabase.table("products").select("price").eq("name", product_name).execute()

    return len(response.data) > 0


if __name__ == "__main__":
    mcp.run()
