<?php

// We can the authentication and host from an ini file in our home directory
$home_dir = $_SERVER['HOME'];
$videoai = parse_ini_file("$home_dir/.videoai");
$host = $videoai['host'];

// We get the image from the command-line
$imagefile = $argv[1];
if (!file_exists($imagefile)) {
    print "The image file $imagefile does not exist\n";
    exit(-1);
}

// We do our request for the face-log image
$ch = curl_init();

// We add the image we want to run the face-log on
$post_data = array('image' => new \CURLFile($imagefile));

// Set up the other curl options
curl_setopt($ch, CURLOPT_USERPWD, $videoai['apiKey_id'] . ":" . $videoai['apiKey_secret']);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_VERBOSE, false);
curl_setopt($ch, CURLOPT_URL, $host.'/face_log_image');
curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

print "Submitting FaceLogImage task for image $imagefile\n";
$result = curl_exec($ch);
//print $result;

// The job has been put in a queue.  We just get a bit of data saying that.
$data = json_decode($result, true);
$status = $data['status'];
if($status == 'fail') {
    print "Task failed.\n";
    exit(-1);
}
$task = $data['task'];

$job_id = $task['job_id'];
print 'Waiting for FaceLogImage task with JobId: '.$job_id."\n";

// Now lets wait until the job is done, by asking every 0.5 seconds.....
$ch2 = curl_init();
curl_setopt($ch2, CURLOPT_USERPWD, $videoai['apiKey_id'] . ":" . $videoai['apiKey_secret']);
curl_setopt($ch2, CURLOPT_URL, $host.'/face_log_image/'.$job_id);
curl_setopt($ch2, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch2, CURLOPT_FOLLOWLOCATION, true);
while (!$task['complete']) {
    $result = curl_exec($ch2);
    $data = json_decode($result, true);
    $task = $data['task'];
    usleep (500000);
}

// Job is done, lets see if we found any faces
//print $result;
$number_of_sightings = $task['number_of_sightings'];

for($i=0;$i < $number_of_sightings; $i++) {
    $sighting = $task['sightings'][$i];
    $sighting_id = $sighting['sighting_id'];
    print 'Saving thumbnail of sighting '.$sighting_id."\n";
    file_put_contents($sighting_id.'.jpg', file_get_contents($sighting['thumbnail']));
}

print 'We have found '.$number_of_sightings.' faces in the image '.$imagefile."\n";

?>