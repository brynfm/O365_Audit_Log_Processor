import os, os.path
from flask import Flask, Blueprint, render_template, request, url_for, redirect, flash, send_file
from data_handlers import o365_handler

data_blueprint = Blueprint('file', __name__)


base_path = os.path.dirname(os.path.realpath(__file__))
base_path = os.path.dirname(base_path)

upload_path = os.path.normpath(os.path.join(base_path, 'static/assets/csv_files/'))
process_path = os.path.normpath(os.path.join(base_path, 'static/assets/csv_export/'))


@data_blueprint.route('/', methods=['GET', 'POST'])
def file_index():

    if request.method == 'POST':
        temp = o365_handler.o365()
        temp.file_parser()
        flash(f'Files Processed', 'success')
        return redirect(url_for('file.file_index'))

    u_files = []
    p_files = []

    for u_file in os.listdir(upload_path):
        filename = str(u_file)
        u_files.append(filename)

    for p_file in os.listdir(process_path):
        filename = str(p_file)
        p_files.append(filename)

    return render_template('file/file_index.html', u_files=u_files, p_files=p_files, title='Files')


@data_blueprint.route('/process/download/<string:p_file>', methods=['GET', 'POST'])
def download_process_file(p_file):
    path = os.path.normpath(os.path.join(process_path, p_file))
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return redirect(url_for('file.file_index'))


@data_blueprint.route('/upload/delete/<string:u_file>', methods=['GET', 'POST'])
def delete_uploaded_file(u_file):
    file_path = os.path.normpath(os.path.join(upload_path, u_file))
    os.remove(file_path)
    flash(f'{u_file} Deleted', 'success')
    return redirect(url_for('file.file_index'))


@data_blueprint.route('/process/delete/<string:p_file>', methods=['GET', 'POST'])
def delete_process_file(p_file):
    file_path = os.path.normpath(os.path.join(process_path, p_file))
    os.remove(file_path)
    flash(f'{p_file} Deleted', 'success')
    return redirect(url_for('file.file_index'))