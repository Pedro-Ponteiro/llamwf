import requests
from PIL import Image

from llam_cli.inference import run_inference
from llam_cli.screenshot_taker import ScreenshotTaker
from llam_cli.usb_comm import open_usb_port, read_data_from_usb, send_data_to_usb


def get_dummy_image():
    img_url = (
        "https://storage.googleapis.com/sfr-vision-language-research/BLIP/demo.jpg"
    )
    raw_image = Image.open(requests.get(img_url, stream=True).raw).convert("RGB")
    return raw_image


def main():
    # Abre a conexão com o microcontrolador

    serial_leo = open_usb_port()
    st = ScreenshotTaker()
    image = st.take_screenshot_of_window("Notepad")

    while True:
        # Lê os dados do microcontrolador (URL da imagem e pergunta)

        # TODO: fazer screenshot

        system_prompt = run_inference("human", infos="""MINHAS INFOS AQUI""")
        ceo_commands = run_inference(
            "ceo",
            system_prompt=system_prompt,
            database="./database",
            llam_comm_folder="./llam_comm",
        )

        if not ceo_commands:
            # Caso não haja dados, continue aguardando
            # TODO: BUGOOOU
            exit()

        run_inference(
            "tech_lead",
            system_prompt=system_prompt,
            database="./database",
            llam_comm_folder="./llam_comm",
            llam_comm_only=True,
        )

        run_inference(
            "programmer",
            system_prompt=system_prompt,
            database="./database",
            llam_comm_folder="./llam_comm",
            llam_comm_only=True,
        )

        tasks_pending = "1"

        while tasks_pending:

            programmer_execution_status = run_inference(
                "programmer",
                system_prompt=system_prompt,
                database="./database",
                llam_comm_folder="./llam_comm",
                llam_comm_only=True,
            )
            tasks_pending = not programmer_execution_status["task_completed"]

        # Envia a resposta de volta
        # send_data_to_usb(serial_leo, answer)


if __name__ == "__main__":
    main()
