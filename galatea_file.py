# This file is part galatea_file blueprint for Flask.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from flask import Blueprint, Response, abort, current_app, redirect
from galatea.tryton import tryton
from mimetypes import guess_type

galatea_file = Blueprint('galatea_file', __name__, template_folder='templates')

Attachment = tryton.pool.get('ir.attachment')
StaticFile = tryton.pool.get('galatea.static.file')

RESOURCE = current_app.config.get('TRYTON_ATTACHMENT_RESOURCE')


@galatea_file.route('/file/<path:file_uri>', endpoint="file")
@tryton.transaction()
def filename(file_uri):
    file_uri = file_uri.split('/')
    if len(file_uri) not in (1, 2):
        abort(404)

    if len(file_uri) == 2:
        directory, filename = file_uri
        static_file_domain = [
            ('folder.name', '=', directory),
            ('name', '=', filename),
            ]
    else:
        filename = file_uri[0]
        static_file_domain = [
            ('name', '=', filename),
            ]

    static_files = StaticFile.search(static_file_domain, limit=1)
    if static_files:
        if static_files[0].type == 'remote':
            return redirect(static_files[0].remote_path)

        file_mime = guess_type(filename)[0]
        return Response(static_files[0].file_binary, mimetype=file_mime)

    attachments = Attachment.search([
        ('name', '=', filename),
        ('allow_galatea', '=', True),
        ], limit=1)
    if not attachments:
        abort(404)
    attachment, = attachments
    resource = str(attachment.resource)
    if not resource.split(',')[0] in RESOURCE:
        abort(404)

    if attachment.type == 'link':
        if not attachment.link:
            abort(404)
        return redirect(attachment.link)

    file_mime = guess_type(filename)[0]
    return Response(attachment.data, mimetype=file_mime)
