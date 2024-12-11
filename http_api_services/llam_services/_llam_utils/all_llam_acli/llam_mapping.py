import llam_acli.inference_services.vision_qa.blip_model_run as blip_model_run


def run_inference(
    llm_model: str = ("vision_qa", "tech_lead", "swe", "automated_human", "ceo"),
    **kwargs
) -> dict[str, str]:
    # Baixa a imagem (idealmente cachear se for a mesma)

    if llm_model == "vision_qa":

        img_info = blip_model_run.get_info_from_image(
            kwargs["image"], kwargs["question"]
        )

        return img_info

    elif llm_model == "tech_lead":
        ...
        # open source with prompt engineering
    elif llm_model == "programmer":
        ...
        # open source with prompt engineering
    elif llm_model == "human":
        ...
    elif llm_model == "ceo":
        ...
