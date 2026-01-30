from flask import render_template, request, redirect, url_for
from testapp import app
import pymysql
import time
import logging
from contextlib import contextmanager
from werkzeug.utils import secure_filename
import os
from PIL import Image, ImageFilter, ImageMath
import uuid
import qrcode

@app.route('/')
def mainpage_UUID(UUID):
    return render_template('testapp/mainpage.html', UUID=UUID)

