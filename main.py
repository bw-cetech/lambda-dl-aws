import serverless_wsgi

import flask
from flask import request, redirect, flash, url_for, abort

import boto3
import io
import pybase64

import imghdr
import os

from python.dlmodel import Model

from werkzeug.utils import secure_filename

from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

from tensorflow.keras.preprocessing.image import load_img, img_to_array

main = flask.Flask(__name__)
main.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 # increased as bad request with large images
main.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.gif']
main.config['UPLOAD_FOLDER'] = '/tmp/'

def validate_image(stream):
    header = stream.read(1024)  # increased from 512 as bad request with large images
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + format # (format if format != 'jpeg' else 'jpg') ASSUMES JPEG AND JPG FORMAT CAN BOTH BE UPLOADED

def write_image_to_s3(myImg, bucket, key, region_name='eu-west-1'):
    """Write an image array into S3 bucket

    Parameters
    ----------
    bucket: string
        Bucket name
    key : string
        Path in s3

    Returns
    -------
    None
    """
    s3 = boto3.resource('s3', region_name)
    bucket = s3.Bucket(bucket)
    object = bucket.Object(key)
    object.put(Body=myImg, ContentType='image/png') 

def read_image_from_s3(bucket, key, region_name='eu-west-1'):
    """Load image file from s3.

    Parameters
    ----------
    bucket: string
        Bucket name
    key : string
        Path in s3

    Returns
    -------
    np array
        Image array
    """
    
    s3 = boto3.resource('s3', region_name=region_name)
    bucket = s3.Bucket(bucket)
    object = bucket.Object(key)
    response = object.get()
    file_stream = response['Body']
    im = Image.open(file_stream)
    return im

@main.route('/')
def index():
    return flask.render_template('index.html')

@main.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        """ if file_ext not in main.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            abort(400) """ # removed validation for now, can test as a post-process
      
        myBucket = 'serverless-flask-contain-serverlessdeploymentbuck-p3youfljn9jy'
        myKey = 'serverless/serverless-flask-container-new/uplImg.png'
        write_image_to_s3(uploaded_file, myBucket, myKey, region_name='eu-west-1')

        print("uploaded image to S3")
        myImg = read_image_from_s3(myBucket, myKey, region_name='eu-west-1')

        myImg = myImg.resize((224,224))
        myImg_array = img_to_array(myImg)
   
        model = Model()

        return flask.render_template("index.html", token=model.runInference(myImg_array))
        
    return redirect(url_for('index'))

def handler(event, context):
    return serverless_wsgi.handle_request(main, event, context)
