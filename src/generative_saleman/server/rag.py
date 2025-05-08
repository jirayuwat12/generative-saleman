# server.py
from mcp.server.fastmcp import FastMCP
import sys
import requests
# Create an MCP server
mcp = FastMCP(
    name="mcp-boardgame-rag",
    dependencies=["requests"],
    description="A tool to search for board games based on user queries.",
    version="0.0.1",
)


# Add an addition tool
@mcp.tool()
def search_board_game(prompt: str, top_n: int = 3) -> list:
    """
    Search for a board game based on a user's description.

    Parameters:
        prompt (str): A question or query, ideally asking for board game suggestions or themes.
                      Example: "มีบอร์ดเกมอะไรที่ดัดแปลงมาจากการ์ตูนญี่ปุ่นเกี่ยวกับการสำรวจดันเจียนบ้าง?"
        top_n (int): The number of top relevant documents to return. Default is 3.

    Returns:
        list: A list of board game documents, each with the following structure:
            str          # A formatted string containing the board game title, meta data, and description

    Example result:
        [
            "Title: Monster Eater Dungeon Meshi (TH) มอนสเตอร์อีทเตอร์ สูตรลับตำรับดันเจียน\nMeta data: ประเภทบอร์ดเกม : ครอบครัว อายุ : 10+ จำนวนผู้เล่น : 2-5 คน เวลา : 45 นาที\nOriginal price: ฿1,450.00\nDiscount price: N/A\nAdditional price: N/A\nURL: https://siamboardgames.com/product/monster-eater-dungeon-meshi-th/\nContent: ในเกมนี้ผู้เล่นจะได้เข้าไปสู่โลกของสูตรลับตำรับดันเจียน การ์ตูนดังจากญี่ปุ่นที่มีธีมเกี่ยวกับการสำรวจดันเจียนเพื่อเป้าหมายที่แตกต่างกันไปในเวอร์ชั่นบอร์ดเกม ผู้เล่นจะได้สวมบทบาทเป็นหนึ่งในหัวหน้าจากปาร์ตี้ ไลออส, ชูโร่, ทันซ์, คาบรู และ กองทัพคานาเรีย ที่มีเป้าหมายในการสำรวจดันเจียนให้ถึงชั้นล่างสุดและกำจัดบอสลงให้ได้ ในดันเจียนนั้นแบ่งออกเป็น 2 ชั้น คือชั้นบนและชั้นล่าง ในระหว่างทางของการสำรวจดันเจียน ผู้เล่นจะได้พบเจอกับมอนสเตอร์,ไอเทม,เหตุการณ์พิเศษมากมาย และหากมีผู้สำรวจดันเจียนชั้นบนได้ครบ 100% บอสประจำชั้น คิเมร่าฟาลิน จะปรากฎตัวออกมาเพื่อขวางทางการลงสู่ดันเจียนชั้นล่าง ผู้เล่นจะต้องปราบบอสลงให้ได้ และลงไปสำรวจชั้นล่างต่อให้ครบ 100% อีกครั้ง เพื่อให้บอสตัวสุดท้าย จอมเวทคลั่งทิสเซิล ปรากฎตัวและปราบลงให้จงได้ เพื่อเป็นการจบเกมคะแนนจากเกมนี้จะมาจาก ไอเทม, มอนสเตอร์ (ที่ปรุงอาหารสำเร็จ), มอนสเตอร์ระดับบอส และ โทเคนเงินแต่หากผู้เล่นสำรวจดันเจียนชั้นล่างได้ไม่ครบ 100% ก็ถูกหักคะแนนด้วยเช่นกันผู้เล่นที่มีคะแนนสูงที่สุดจะเป็นผู้ชนะเกม และได้รับการขนานนามเป็นผู้พิชิตดันเจียน!\nAdditional Info: น้ำหนัก: 1.5 กก.; ขนาด: 20 × 20 × 8 เซนติเมตร\nBox Contents: การ์ดดันเจียน 125 ใบ, การ์ดตัวละคร 28 ใบ, การ์ดมอนสเตอร์ 30 ใบ, การ์ดบอสมอนสเตอร์ 2 ใบ, การ์ดไอเท็ม 20 ใบ, การ์ดขั้นตอนการเล่น 5 ใบ, แผ่นดันเจี้ยนชั้นบน/ชั้นล่าง 5 แผ่น, โทเคนอาหารและเงิน 53 ชิ้น, โทเคนเวทย์มนต์ 36 ชิ้น, โทเคนดาบ 1 ชิ้น, ลูกเต๋า 6 ลูก, คู่มือเกม 1 เล่ม\nSleeve Contents: ซองใส่การ์ด: White Diamond Lily, ขนาดซอง: 63.5 x 88 มม., จำนวน: 210 ซอง / 5 แพค\n,
            ...
        ]

    Notes:
        - This tool should only be used for Thai-language prompts specifically related to board games.
        - Double-check the response to ensure it is relevant to the prompt; if not, adjust the prompt and try again.
        - If you want to search for board game expansions or extensions, consider increasing top_n to 5 or more.
    """
    response = requests.post(
        "http://localhost:5001/completions",
        json={"prompt": prompt, "top_n": top_n}
    )
    
    return response.json()["top_documents"]


# # Add a dynamic greeting resource
# @mcp.resource("greeting://{name}")
# def get_greeting(name: str) -> str:
#     """Get a personalized greeting"""
#     return f"Hello, {name}!"
if __name__ == "__main__":
    mcp.run()
