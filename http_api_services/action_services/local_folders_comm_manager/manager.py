import os
import shutil
from pathlib import Path


class LocalFoldersCommManager:
    def __init__(
        self,
        base_path: str = "./http_api_services/llam_services/_llam_utils/local_llam_comm",
    ):
        self.base_path = Path(base_path)

        self.file_config = {
            "img": {
                "allowed_exts": [".jpeg", ".jpg", ".png"],
            },
            "script": {
                # Scripts podem ter qualquer extensão de texto.
                # Vamos assumir qualquer extensão não binária enviada pelo cliente.
                "default_ext": ".txt"
            },
            "info": {"ext": ".txt"},
            "task": {"ext": ".txt"},
        }

    def handle_operation(
        self,
        operation: str,
        folder_name: str,
        file_type: str,
        filename: str = None,
        content: str = None,
        status: str = None,
        autor: str = None,
        data: str = None,
        titulo: str = None,
        tipo: str = None,
        recursive: bool = False,
        script_ext: str = None,
    ):
        """
        Operações suportadas:
          - create: cria um novo arquivo
          - update: atualiza um arquivo existente
          - delete: deleta um arquivo existente
          - list: lista a estrutura da pasta

        folder_name: nome da pasta onde a operação será realizada
        file_type: 'img', 'script', 'info', 'task'
        filename: nome do arquivo (opcional para create, obrigatório para update/delete)
        content: no caso de img, é um path para uma imagem existente; para textuais, é o conteúdo de texto.
        status: usado para 'task' (opcional, adiciona "STATUS:..." no início do arquivo)
        autor, data, titulo, tipo: usado para gerar um filename se não for fornecido.
        recursive: se True, a listagem é recursiva para pastas
        script_ext: extensão opcional a ser usada para script caso não seja dado filename.
        """

        # Verifica se o tipo de arquivo é suportado
        if file_type not in self.file_config:
            raise ValueError("Unsupported file type")

        folder_path = self.base_path / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        # Operações
        if operation == "create":
            file_path = self._prepare_new_file_path(
                folder_path, file_type, filename, autor, data, titulo, tipo, script_ext
            )
            return self._create(file_path, file_type, content, status)

        elif operation == "update":
            if not filename:
                raise ValueError("filename is required for update")
            file_path = folder_path / filename
            return self._update(file_path, file_type, content, status)

        elif operation == "delete":
            if not filename:
                raise ValueError("filename is required for delete")
            file_path = folder_path / filename
            return self._delete_file(file_path)

        elif operation == "list":
            # Listar a pasta (e subpastas se recursive=True)
            structure_str = self._list_directory(folder_path, recursive)
            return {"message": "ok", "structure": structure_str}
        else:
            raise ValueError("Unsupported operation")

    def _prepare_new_file_path(
        self, folder_path, file_type, filename, autor, data, titulo, tipo, script_ext
    ):
        # Se já houver filename, usa-se ele diretamente.
        # Caso contrário, gera-se um novo com base em autor, data, titulo, tipo e extensão.
        if filename:
            return folder_path / filename

        # Determina a extensão
        ext = self._determine_extension(file_type, script_ext)

        if not (autor and data and titulo and tipo):
            raise ValueError(
                "autor, data, titulo, tipo are required to generate a new filename when filename is not provided."
            )

        new_filename = f"{autor}_{data}_{titulo}_{tipo}{ext}"
        return folder_path / new_filename

    def _determine_extension(self, file_type, script_ext):
        if file_type == "img":
            # Extensão será determinada a partir do conteúdo no momento do create/update,
            # mas aqui precisamos de algo default. Se não soubermos ainda, deixamos .png
            # Porém, o ideal é só decidir a extensão no momento do write, após verificar o content.
            # Aqui, vamos colocar um placeholder e ajustar no _create_image/_update_image.
            return ""
        elif file_type == "script":
            return (
                script_ext if script_ext else self.file_config["script"]["default_ext"]
            )
        elif file_type in ["info", "task"]:
            return self.file_config[file_type]["ext"]
        else:
            raise ValueError("Invalid file type for extension determination")

    def _create(self, file_path, file_type, content, status):
        if file_type == "img":
            return self._create_image(file_path, content)
        else:
            return self._create_text_file(file_path, file_type, content, status)

    def _update(self, file_path, file_type, content, status):
        if not file_path.exists():
            return {"error": "File not found"}

        if file_type == "img":
            return self._update_image(file_path, content)
        else:
            return self._update_text_file(file_path, file_type, content, status)

    # CREATE/UPDATE para IMG
    def _create_image(self, file_path, content):
        # content é um filepath de uma imagem existente
        if content is None or not os.path.exists(content):
            return {"error": "Invalid image content path"}

        # Verifica extensão
        source_ext = Path(content).suffix.lower()
        if source_ext not in self.file_config["img"]["allowed_exts"]:
            return {"error": f"Unsupported image extension: {source_ext}"}

        # Ajusta o file_path com a extensão correta
        if file_path.suffix == "":
            file_path = file_path.with_suffix(source_ext)

        shutil.copy(content, file_path)
        relative_path = str(file_path.relative_to(self.base_path))
        return {"message": "Image created", "filename": relative_path}

    def _update_image(self, file_path, content):
        if content is None or not os.path.exists(content):
            return {"error": "Invalid image content path"}

        source_ext = Path(content).suffix.lower()
        if source_ext not in self.file_config["img"]["allowed_exts"]:
            return {"error": f"Unsupported image extension: {source_ext}"}

        # Mesmo que a extensão seja diferente, mantemos o file_path existente.
        # Se desejar sobrescrever a extensão, poderíamos renomear, mas não foi especificado.
        shutil.copy(content, file_path)
        relative_path = str(file_path.relative_to(self.base_path))
        return {"message": "Image updated", "filename": relative_path}

    # CREATE/UPDATE para TEXTOS
    def _create_text_file(self, file_path, file_type, content, status):
        # Determina a extensão correta se ainda estiver vazia
        if file_path.suffix == "" and file_type in ["info", "task"]:
            file_path = file_path.with_suffix(".txt")
        elif file_type == "script" and file_path.suffix == "":
            # Se script, já deveria ter sido definido acima
            file_path = file_path.with_suffix(".txt")  # fallback final

        if content is None:
            content = ""

        if status and file_type == "task":
            content = f"STATUS:{status}\n{content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        relative_path = str(file_path.relative_to(self.base_path))
        return {"message": "File created", "filename": relative_path}

    def _update_text_file(self, file_path, file_type, content, status):
        # Lê o conteúdo antigo se necessário
        with open(file_path, "r", encoding="utf-8") as f:
            old_content = f.read()

        # Se content for None, mantém o antigo
        new_content = content if content is not None else old_content

        if status and file_type == "task":
            # sobrescreve o status no topo do arquivo
            new_content = f"STATUS:{status}\n{new_content}"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        relative_path = str(file_path.relative_to(self.base_path))
        return {"message": "File updated", "filename": relative_path}

    # DELETE
    def _delete_file(self, file_path):
        if file_path.exists():
            file_path.unlink()
            relative_path = str(file_path.relative_to(self.base_path))
            return {"message": "File deleted", "filename": relative_path}
        return {"error": "File not found"}

    # LISTAR DIRETÓRIO
    def _list_directory(self, folder_path: Path, recursive: bool) -> str:
        # Retorna uma string formatada com a estrutura de pastas e arquivos
        # Se recursive=False, só lista o diretório atual
        # Se recursive=True, faz uma listagem recursiva tipo árvore

        if not folder_path.exists():
            return f"Folder {folder_path} not found."

        structure_lines = []
        base_level = len(folder_path.parts)

        if recursive:
            for root, dirs, files in os.walk(folder_path):
                level = len(Path(root).parts) - base_level
                indent = "    " * level
                structure_lines.append(f"{indent}{Path(root).name}/")
                sub_indent = "    " * (level + 1)
                for f in files:
                    structure_lines.append(f"{sub_indent}{f}")
        else:
            structure_lines.append(f"{folder_path.name}/")
            for item in folder_path.iterdir():
                if item.is_dir():
                    structure_lines.append(f"    {item.name}/")
                else:
                    structure_lines.append(f"    {item.name}")

        return "\n".join(structure_lines)
