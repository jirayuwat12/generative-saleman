from mcp.server.fastmcp import FastMCP

# Create a FastMCP object
mcp = FastMCP(name="generative-saleman-product-info")

# Create constants
PRODUCT_NAME_TO_PRICE = {"apple": 55.0, "banana": 5.0, "orange": 35.0, "grape": 45.0, "watermelon": 25.0}


# Add get product price tool
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
    if product_name not in PRODUCT_NAME_TO_PRICE:
        return None
    return PRODUCT_NAME_TO_PRICE[product_name]


if __name__ == "__main__":
    mcp.run()
