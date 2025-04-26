from src.generative_saleman.services.qr_services import decode_slip, verify_slip, generate_qr_code
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> FastMCP:
    @mcp.tool(name="generate_qr", description="สร้าง QR Payment และส่งรูป QR เป็น base64")
    def generate_qr(amount: float) -> dict:
        """
        Generate a PromptPay QR Code for payment.

        Args:
            amount (float): The amount (in Thai Baht) that the customer needs to pay.

        Returns:
            dict:
                - "qr_base64" (str): The base64-encoded PNG image of the generated QR code.
                - "info" (str): Additional payment information for the user.

        Example:
            >>> generate_qr(350)
            {
                'qr_base64': 'iVBORw0KGgoAAAANSUhEUgAAA...',
                'info': 'ชำระเงินจำนวน 350 บาท ผ่าน QR ด้านล่าง เบอร์ PromptPay 0613261566'
            }
        """
        phone_nbr = "0613261566"
        qr_base64 = generate_qr_code(phone_nbr=phone_nbr, amount=amount)
        return {"qr_base64": qr_base64, "info": f"ชำระเงินจำนวน {amount} บาท ผ่าน QR ด้านล่าง เบอร์ PromptPay {phone_nbr}"}

    @mcp.tool(name="decode_slip", description="Decode slip and verify payment")
    def decode_slip_and_verify(slip_base64: str, amount: float) -> dict:
        """
        Decode a base64-encoded slip image and verify the payment.

        Args:
            slip_base64 (str): The base64-encoded slip image.
            amount (float): The expected amount for verification.

        Returns:
            dict:
                - "ref_nbr" (str): The reference number extracted from the slip.
                - "status" (str): The status of the payment verification.
                - "message" (str): Additional information about the verification result.

        Example:
            >>> decode_slip_and_verify('iVBORw0KGgoAAAANSUhEUgAAA...', 350)
            {
                'ref_nbr': '1234567890',
                'status': 'success',
                'message': 'Payment verified successfully.'
            }
        """
        ref_nbr = decode_slip(slip_base64)
        if ref_nbr is None:
            return {"ref_nbr": None, "status": "error", "message": "Invalid slip image."}
        try:
            response = verify_slip(ref_nbr=ref_nbr, amount=str(amount))
            return {
                "ref_nbr": ref_nbr,
                "status": response["status"],
                "message": response["message"],
            }
        except Exception as e:
            return {"ref_nbr": ref_nbr, "status": "error", "message": str(e)}

    return mcp


if __name__ == "__main__":
    mcp = FastMCP(
        name="generative-saleman-payment-solution",
        dependencies=["supabase", "dotenv"],
        description="A tool to get payment solution.",
        version="0.0.1",
    )
    mcp = register(mcp)
    mcp.run()
