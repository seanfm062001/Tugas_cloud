import json
from nameko.rpc import RpcProxy
from nameko.web.handlers import http
from werkzeug.wrappers import Response
import uuid

from dependencies import SessionProvider


from itertools import permutations 
from itertools import combinations

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'data/cloud'


if not os.path.exists('data'):
    os.mkdir('data')
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

class GatewayService:
    name = 'gateway'

    user_rpc = RpcProxy('user_service')
    cloud_rpc = RpcProxy('cloud_service')
    session_provider = SessionProvider()

    @http('POST', '/register')
    def add_user(self, request):
        result = request.json
        user = result ["username"]
        kunci = result ["password"]
        nambahroom = self.user_rpc.add_user(user,kunci)
        return nambahroom

    @http('GET', '/logout')
    def logout_user(self, request):
        cookies = request.cookies
        if cookies:
            response = Response('success')
            response.delete_cookie('SESSID')
            self.session_provider.delete_session(cookies['SESSID'])
            return response
        else:
            response = Response('You need to Login First')
            return response

    @http('POST', '/login')
    def check_user(self, request):
        result = request.json
        user_data = {
            'username': result['username'],
            'password': result['password']
        }
        cekuser = self.user_rpc.check_user(user_data)
        if cekuser== 1 :
            session_id = self.session_provider.set_session(user_data)
            response = Response(str(user_data))
            response.set_cookie('SESSID', session_id)
            return response
        
        else :
             return "username atau password salah"

    
        
    @http('POST', '/upload')
    def upload_user(self, request):
        cookies = request.cookies
        if cookies:
            session_data = self.session_provider.get_session(cookies['SESSID'])
            nama = session_data['username']
            arrnamafile = []
            files = request.files.getlist('file')
            for file in files:
                app = Flask(__name__)
                app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                arrnamafile.append(filename)
                
            cloudupload = self.cloud_rpc.upload(arrnamafile,nama)
            return cloudupload

        else:
            response = Response('You need to Login First')
            return response

    @http('GET', '/download/<int:idgambar>')
    def download_user(self, request,idgambar):
        gambarid = idgambar
        cookies = request.cookies
        if cookies:
            session_data = self.session_provider.get_session(cookies['SESSID'])
            nama = session_data['username']
            file = self.cloud_rpc.download(nama,gambarid)
            filename = file['filename']
            response = Response(open(UPLOAD_FOLDER + '/' + filename, 'rb').read())
            response.headers['Content-Type'] = "image/jpeg"
            response.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)
            return response
        else:
            response = Response('You need to Login First')
            return response
    