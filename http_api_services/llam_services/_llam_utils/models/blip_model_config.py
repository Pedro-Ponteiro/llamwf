from transformers import BlipForQuestionAnswering, BlipProcessor


def get_blip_processor():

    # Carrega o processador (tokenizer e processador de imagem)
    return BlipProcessor.from_pretrained(
        "Salesforce/blip-vqa-base", cache_dir="./models/blip_cache_processor"
    )


def get_blip_model():
    # Carrega o modelo já na GPU (se disponível)
    return BlipForQuestionAnswering.from_pretrained(
        "Salesforce/blip-vqa-base", cache_dir="./models/blip_cache_model"
    ).to("cuda")
