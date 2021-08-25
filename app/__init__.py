from flask import Flask

app = Flask(__name__)


from environs import Env
from os import environ
import os

from kenzie.image import upload_by_form, list_all_files, files_by_type, download_file, download_file_zip

env = Env()
env.read_env()
FILES_DIRECTORY = environ.get('FILES_DIRECTORY')
MAX_CONTENT_LENGTH = int(environ.get('MAX_CONTENT_LENGTH'))

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


if not os.path.exists(FILES_DIRECTORY):
    os.makedirs(FILES_DIRECTORY)

@app.errorhandler(413)
def error_function(_):
    return {'message': 'Arquivo maior que o esperado.'}, 413

@app.route('/upload', methods=['POST'])
def upload():
    return upload_by_form()


@app.route('/files', methods=['GET'])
def list_files():
    return list_all_files()

@app.route('/files/<string:type>', methods=['GET'])
def list_files_by_type(type: str):
    return files_by_type(type)


@app.route('/download/<file_name>', methods=['GET'])
def download(file_name: str):
    return download_file(file_name)


@app.route('/download-zip', methods=['GET'])
def download_zip():
    return download_file_zip()
