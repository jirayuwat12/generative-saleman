from mcp.server.fastmcp import FastMCP

# Create a FastMCP object
mcp = FastMCP(name="generative-saleman-product-info")

# Create constants
PRODUCT_NAME_TO_PRICE = {
    'apple': 55.0,
    'banana': 5.0,
    'orange': 35.0,
    'grape': 45.0,
    'watermelon': 25.0
} 

# Add sum_total_price tool
@mcp.tool()
def sum_total_price(product_list: list[tuple[str, int]]) -> float:
    """
    Calculate the total price of a list of products.

    :param product_list: A list of product names which in form (product_name, quantity).
    :type product_list: list[tuple[str, int]]
    
    :return: The total price of the products.
    :rtype: float

    ## Example
    > sum_total_price([('apple', 1), ('banana', 1)])
    60.0
    > sum_total_price([('grape', 1), ('watermelon', 2)])
    95.0
    """
    total_price = 0
    for product, quantity in product_list:
        total_price += PRODUCT_NAME_TO_PRICE.get(product, 0) * quantity
    return total_price


# Add get product price tool
@mcp.tool()
def get_product_price(product_name: str) -> float:
    """
    Get the price of the given product name and raise error if there's no the product

    :param product_name: The name of the product.
    :type product_name: str

    :return: The price of the product.
    :rtype: float

    :raises ValueError: If the product name is not in the PRODUCT_NAME_TO_PRICE dictionary.

    ## Example
    > get_product_price('apple')
    55.0
    > get_product_price('banana')
    5.0
    > get_product_price('no-product')
    raise ValueError
    """
    if product_name not in PRODUCT_NAME_TO_PRICE:
        raise ValueError(f'Product {product_name} is not found.')
    return PRODUCT_NAME_TO_PRICE[product_name]

if __name__ == "__main__":
    mcp.run()
