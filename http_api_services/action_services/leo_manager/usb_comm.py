import json
import logging
import time
from typing import Union

import serial

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


class USBLeoSerial:
    def __init__(
        self, port: str = "COM3", baud_rate: int = 115200, timeout: float = 1.0
    ):
        """
        Inicializa a classe USBLeoSerial e abre a porta serial.

        Args:
            port (str): Nome da porta serial (e.g., "COM3" ou "/dev/ttyACM0").
            baud_rate (int): Taxa de baud da comunicação.
            timeout (float): Tempo de timeout para operações de leitura/escrita.
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.ser = None
        self.open_usb_port()

    @staticmethod
    def is_valid_json(json_str: str) -> bool:
        """
        Verifica se uma string é um JSON válido.

        Args:
            json_str (str): String a ser verificada.

        Returns:
            bool: True se for JSON válido, False caso contrário.
        """
        try:
            json.loads(json_str)
            return True
        except ValueError:
            return False

    def open_usb_port(self) -> None:
        """
        Abre a porta serial para comunicação com o dispositivo.
        """
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
            # Aguarda a estabilização da conexão
            time.sleep(2)
            logging.info(f"Porta {self.port} aberta com sucesso.")
        except serial.SerialException as e:
            logging.error(f"Erro ao abrir a porta serial {self.port}: {e}")
            raise

    def read_clipboard(self) -> Union[dict, str, None]:
        """
        Lê o conteúdo do clipboard do dispositivo conectado pela porta serial.

        Returns:
            Union[dict, str, None]: Retorna um dicionário caso o conteúdo seja JSON válido,
            uma string caso seja texto não JSON, ou None em caso de falha.
        """
        if not self.ser or not self.ser.is_open:
            logging.error("Porta serial não está aberta.")
            return None

        try:
            lines = self.ser.readlines()
            # readlines retorna uma lista de bytes, é necessário decodificar
            clipboard_str = b"".join(lines).decode("utf-8").strip()
            if not clipboard_str:
                logging.warning("Nenhum dado lido do dispositivo.")
                return None
            # Tenta interpretar o conteúdo como JSON
            try:
                data = json.loads(clipboard_str)
                logging.info("Clipboard lido e interpretado como JSON.")
                return data
            except json.JSONDecodeError:
                logging.info("Clipboard lido como string não-JSON.")
                return clipboard_str
        except Exception as e:
            logging.error(f"Erro ao ler clipboard do dispositivo: {e}")
            return None

    def send_mouse_commands(self, commands_json: str) -> bool:
        """
        Envia comandos de mouse em formato JSON para o microcontrolador.

        Args:
            commands_json (str): Comandos em formato JSON a serem enviados.

        Returns:
            bool: True se enviados com sucesso, False em caso de falhas.
        """
        if not self.is_valid_json(commands_json):
            logging.error("Comandos de mouse inválidos. Não é um JSON válido.")
            return False

        if not self.ser or not self.ser.is_open:
            logging.error("Porta serial não está aberta.")
            return False

        try:
            result = self.ser.write((commands_json + "\n").encode("utf-8"))
            if result > 0:
                logging.info(f"Comandos de mouse enviados: {commands_json}")
                return True
            else:
                logging.error("Falha ao enviar comandos de mouse.")
                return False
        except Exception as e:
            logging.error(f"Erro ao enviar comandos de mouse: {e}")
            return False

    def send_keyboard_commands(self, commands_json: str) -> bool:
        """
        Envia comandos de teclado em formato JSON para o microcontrolador.

        Args:
            commands_json (str): Comandos em formato JSON a serem enviados.

        Returns:
            bool: True se enviados com sucesso, False em caso de falhas.
        """
        if not self.is_valid_json(commands_json):
            logging.error("Comandos de teclado inválidos. Não é um JSON válido.")
            return False

        if not self.ser or not self.ser.is_open:
            logging.error("Porta serial não está aberta.")
            return False

        try:
            result = self.ser.write((commands_json + "\n").encode("utf-8"))
            if result > 0:
                logging.info(f"Comandos de teclado enviados: {commands_json}")
                return True
            else:
                logging.error("Falha ao enviar comandos de teclado.")
                return False
        except Exception as e:
            logging.error(f"Erro ao enviar comandos de teclado: {e}")
            return False

    def send_config_commands(self, config_command_json: str) -> bool:
        """
        Recebe um comando de configuração em JSON para alterar o modo HID do microcontrolador.

        Args:
            config_command_json (str): Comando de configuração (e.g. {"mode":1} para teclado, {"mode":2} para mouse).

        Returns:
            bool: True se enviado com sucesso, False em caso de falhas.
        """
        if not self.is_valid_json(config_command_json):
            logging.error("Comando de configuração inválido. Não é um JSON válido.")
            return False

        if not self.ser or not self.ser.is_open:
            logging.error("Porta serial não está aberta.")
            return False

        try:
            result = self.ser.write((config_command_json + "\n").encode("utf-8"))
            if result > 0:
                logging.info(f"Configuração HID enviada: {config_command_json}")
                return True
            else:
                logging.error("Falha ao enviar configuração HID.")
                return False
        except Exception as e:
            logging.error(f"Erro ao enviar comando de configuração: {e}")
            return False

    def close_usb_port(self) -> None:
        """
        Fecha a porta serial.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            logging.info("Porta serial fechada com sucesso.")
        else:
            logging.warning("A porta serial já está fechada ou não foi aberta.")
