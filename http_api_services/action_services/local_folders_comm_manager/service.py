import sys

import load_dotenv

from http_api_services._http_api_utils.generic_service_initializer import (
    create_flask_service,
)
from http_api_services.action_services.local_folders_comm_manager.manager import (
    LocalFoldersCommManager,
)

load_dotenv.load_dotenv("./env")
print(sys.argv)
exit()


def local_folders_handler(manager, request):
    data = request.get_json()
    operation = data.get("operation")
    folder_name = data.get("folder_name")
    file_type = data.get("file_type")
    filename = data.get("filename")
    content = data.get("content")
    status = data.get("status")
    autor = data.get("autor")
    data_str = data.get("data")
    titulo = data.get("titulo")
    tipo = data.get("tipo")
    recursive = data.get("recursive", False)
    script_ext = data.get("script_ext")

    # Executa a lógica do manager
    result = manager.handle_operation(
        operation=operation,
        folder_name=folder_name,
        file_type=file_type,
        filename=filename,
        content=content,
        status=status,
        autor=autor,
        data=data_str,
        titulo=titulo,
        tipo=tipo,
        recursive=recursive,
        script_ext=script_ext,
    )

    return result


if __name__ == "__main__":
    # Configuração da rota para o serviço local_folders_comm_manager
    routes = [
        {
            "endpoint": "/files-manager",
            "methods": ["POST"],
            "handler": local_folders_handler,
        }
    ]

    app = create_flask_service(LocalFoldersCommManager, routes, port=5000, debug=True)
    # Inicia o servidor Flask
    app.run(port=5000, debug=True)
