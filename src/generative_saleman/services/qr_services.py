import requests
from src.generative_saleman.config import QR_VERIFY_TOKEN
import base64
from io import BytesIO
from PIL import Image
from pyzbar.pyzbar import decode


def decode_slip(slip_base64: str) -> str | None:
    binary_data = base64.b64decode(slip_base64)
    img = Image.open(BytesIO(binary_data))
    decoded_objs = decode(img)
    for obj in decoded_objs:
        return obj.data.decode("utf-8")  # Return ref_nbr
    return None


def verify_slip(ref_nbr: str, amount: str) -> dict:
    url = "https://api.openslipverify.com"
    payload = {"refNbr": ref_nbr, "amount": amount, "token": QR_VERIFY_TOKEN}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to verify slip {response.status_code} {response.text}")
    return response.json()


def qr_binary_to_base64(binary_data: bytes) -> str:
    img = Image.open(BytesIO(binary_data))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_base64


def generate_qr_code(phone_nbr: str, amount: float | None) -> str:
    if amount is None:
        url = f"https://promptpay.io/{phone_nbr}"
    else:
        url = f"https://promptpay.io/{phone_nbr}/{str(amount)}"
    response = requests.get(url)
    if response.status_code == 200:
        return qr_binary_to_base64(response.content)
    else:
        raise Exception(f"Failed to generate QR code {response.status_code} {response.text}")
