# PHP Snippets

In this directory are a couple of simple examples of how you can use PHP to access
some of our VideoAI face-recognition services.

You will need a set of developer keys.  The examples also assume you have these keys
stored in your home directory in a file .videoai

~~~
[videoai.net]
apiKey_id = 20LXX95O.....
apiKey_secret = +SMcEtOOfMMq2D24....
host = http://facerec.videoai.net:8000
~~~

## Face Log Image

Run FaceLog on an image and download thumbnails of the faces found.

~~~
php face_log_image_example.php image.jpg
~~~

## Face Authenticate

Authenticate the identity of the faces in two separate images.

~~~
php face_authenticate_example.php image1.jpg image2.jpg
~~~

