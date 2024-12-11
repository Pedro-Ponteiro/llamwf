# generic_service_initializer.py
from flask import Flask, jsonify, request


def create_flask_service(
    manager_cls, route_config, host="0.0.0.0", port=5000, debug=True
):
    """
    Cria uma aplicação Flask genérica a partir de uma classe gerenciadora e um conjunto de rotas.

    Parâmetros:
        manager_cls: Classe do gerenciador que será instanciada.
        route_config: Lista de dicionários com:
            {
                'endpoint': str (ex: '/files'),
                'methods': list (ex: ['POST']),
                'handler': função que recebe (manager, request) e retorna uma resposta (dict ou lista)
            }
        host: Host para rodar o serviço (padrão '0.0.0.0').
        port: Porta para rodar o serviço (padrão 5000).
        debug: Se True, ativa o modo debug do Flask.
    """

    app = Flask(manager_cls.__name__)
    manager = manager_cls()

    for route in route_config:
        endpoint = route.get("endpoint", "/")
        methods = route.get("methods", ["GET"])
        handler_fn = route.get("handler")

        def handle_route():
            try:
                # Chamamos a função handler passando o manager e a request
                response = handler_fn(manager, request)
                return jsonify(response), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        # Registra a rota no Flask
        app.add_url_rule(
            endpoint, endpoint=endpoint, view_func=handle_route, methods=methods
        )

    return app
