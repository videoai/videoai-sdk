<?php
require 'vendor/autoload.php';
use GuzzleHttp\Client;

$api_id = "20LXX959MDATHZQ7Q1Z9EBUFO";
$api_secret = "+SM4eTP1P0QnCNy7/Vy+9XhodoIzrKcEtOOfMMq2D24";
$imagefile = $argv[1];

if (!file_exists($imagefile)) {
    print "The image file $imagefile does not exist\n";
    exit(-1);
}

$client = new Client([
    'base_uri' => 'http://careem.videoai.net:8000',
    'timeout' => 2.0,
    'auth' => [$api_id, $api_secret],
]);

$image_data = ['name' => 'image',
    'filename' => $imagefile,
    'contents' => fopen($imagefile, 'r')];

print "Submitting FaceLogImage task for image $imagefile\n";
$response = $client->request('POST', 'face_log_image', ['multipart' => [$image_data] ]);
//print $response->getBody();

$data = json_decode($response->getBody(), true);

$job_id = $data['task']['job_id'];
print 'Waiting for FaceLogImage task with JobId: '.$job_id."\n";

while (!$data['task']['complete']) {
    $response = $client->request('GET', 'face_log_image/'.$job_id);
    $data = json_decode($response->getBody(), true);
    usleep (500000);
}

//print $response->getBody();
$number_of_sightings = $data['task']['number_of_sightings'];

print 'We have found '.$number_of_sightings.' faces in the image '.$imagefile."\n";






?>