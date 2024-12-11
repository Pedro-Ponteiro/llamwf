from torch import autocast

from models.blip_model_config import get_blip_model, get_blip_processor

# usar no get image from remote window:
# Image.open(response.raw).convert("RGB")


def get_info_from_image(img_pil, question: str):

    processor = get_blip_processor()

    # Prepara a entrada para o modelo
    inputs = processor(img_pil, question, return_tensors="pt").to("cuda")

    with autocast(device_type="cuda"):
        out = get_blip_model().generate(**inputs)

    # Decodifica a resposta
    answer = processor.decode(out[0], skip_special_tokens=True)
    return answer
