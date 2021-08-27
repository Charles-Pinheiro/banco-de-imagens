from flask import request, safe_join, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from environs import Env
from os import environ, path
import os

env = Env()
env.read_env()
FILES_DIRECTORY = environ.get('FILES_DIRECTORY')
MAX_CONTENT_LENGTH = environ.get('MAX_CONTENT_LENGTH')


def upload_by_form():
    '''Faz o upload de um arquivo para um subdiretório específico dentro do diretório
        de uploads.
    
    Returns:
        tupla: Contendo mensagem que tal arquivo foi criado e o status code.
    
    '''

    files_list = list(request.files)

    for file in files_list:

        received_file = request.files[file]

        filename = secure_filename(received_file.filename)

        file_type = filename.split('.')[-1]

        formats_supported_list = ['jpg', 'png', 'gif']

        if file_type not in formats_supported_list:
            return {'message': 'Formato não suportado.'}, 415

        if not os.path.exists(f'{FILES_DIRECTORY}/{file_type}'):
            os.makedirs(f'{FILES_DIRECTORY}/{file_type}')

        file_names = os.listdir(f'{FILES_DIRECTORY}/{file_type}')

        if filename in file_names:
            return {'message': 'Arquivo repetido.'}, 409

        file_path = safe_join(f'{FILES_DIRECTORY}/{file_type}', filename)

        received_file.save(file_path)
    
    return {'message': f'{filename}.'}, 201


def list_all_files():
    '''Lista todos os arquivos que foram feitos upload.

    Returns:
        tupla: Contendo uma lista com o nome de todos os arquivos e o status code.
    '''
    
    files_list = os.walk(FILES_DIRECTORY)

    all_files = []

    for file in list(files_list)[1:]:

        all_files.extend(file[-1])

    return jsonify(all_files), 200


def files_by_type(type: str) -> tuple:
    '''Procura e lista arquivos de determinado tipo de um diretório.

    Args:
        type (str): Palavra representando o tipo do arquivo. (jpg, png, gif)

    Returns:
        tupla: Contendo uma lista com o nome dos arquivos de determinado tipo e o status code.
    '''
    try:
        files_list = os.listdir(f'{FILES_DIRECTORY}/{type}')
        return jsonify(files_list)

    except FileNotFoundError:
        return {'message': 'Diretório não encontrado'}, 404


def download_file(file_name: str):
    '''Faz o download de um arquivo específico.

    Args:
        file_name (str): Palavra representando o nome do arquivo.

    Returns:
        tupla: Contendo o download do arquivo especificado
        (feito pela função send_from_directory do flask) e o status code.
    '''

    type_file = file_name.split('.')[-1]

    path = os.walk(FILES_DIRECTORY)

    if type_file not in list(path)[0][1]:
        return {'message': 'Diretório não encontrado'}, 404
    
    return send_from_directory(directory=f'.{FILES_DIRECTORY}/{type_file}', path=file_name, as_attachment=True), 200


def download_file_zip():
    '''Recebe argumentos via query params e faz o download em zip dos arquivos de
        um diretório específico.

    Args:
        file_type (str): String representando o tipo do arquivo.
        compression_rate (): String representando a taxa de compressão(número) do arquivo.

    Returns:
        tupla: Contendo o download do arquivo especificado
        (feito pela função send_from_directory do flask) e o status code.
    '''

    file_type = request.args.get('file_type')
    compression_rate = request.args.get('compression_rate')

    path_zip = safe_join(f'{FILES_DIRECTORY}', file_type)

    if not os.path.exists(path_zip):
        return {'message': 'Diretório não existe.'}, 404

    if len(os.listdir(path_zip)) == 0:
        return {'message': 'Diretório vazio.'}, 404

    os.system(f' zip -r -{compression_rate} {file_type}.zip {path_zip} ')

    os.system(f'mv {file_type}.zip /tmp')

    return send_from_directory(directory='/tmp', path=f'{file_type}.zip', as_attachment=True), 200
