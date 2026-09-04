import io
import base64
import qrcode
from PIL import Image
from reportlab.platypus import Image as RLImage

def gerar_qrcode_imagem_bytes(dados: str) -> bytes:
    """
    Gera uma imagem PNG de QR Code para os dados informados e retorna os bytes brutos.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(dados)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.getvalue()

def gerar_qrcode_base64(dados: str) -> str:
    """
    Gera uma string base64 para uso direto em tags HTML (<img src="data:image/png;base64,...">).
    """
    img_bytes = gerar_qrcode_imagem_bytes(dados)
    b64_str = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

def gerar_qrcode_flowable(dados: str, width: float = 90, height: float = 90) -> RLImage:
    """
    Gera um flowable RLImage pronto para inserção no documento ReportLab.
    """
    img_bytes = gerar_qrcode_imagem_bytes(dados)
    buffer = io.BytesIO(img_bytes)
    return RLImage(buffer, width=width, height=height)
