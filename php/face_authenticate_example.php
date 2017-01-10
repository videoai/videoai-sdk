<?php

// We can the authentication and host from an ini file in our home directory
$home_dir = $_SERVER['HOME'];
$videoai = parse_ini_file("$home_dir/.videoai");
$host = $videoai['host'];
$service = $host.'/face_authenticate';

// We need the gallery image
$gallery = $argv[1];
if (!file_exists($gallery)) {
    print "The image file $gallery does not exist\n";
    exit(-1);
}

// We get the image from the command-line
$probe1 = $argv[2];
if (!file_exists($probe1)) {
    print "The image file $probe1 does not exist\n";
    exit(-1);
}

// We do our request for the face-log image
$ch = curl_init();

// We add the image we want to run the face-log on
$post_data = array('gallery' => new \CURLFile($gallery),
                   'probe1' => new \CURLFile($probe1));

// Set up the other curl options
curl_setopt($ch, CURLOPT_USERPWD, $videoai['apiKey_id'] . ":" . $videoai['apiKey_secret']);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_VERBOSE, false);
curl_setopt($ch, CURLOPT_URL, $service);
curl_setopt($ch, CURLOPT_POSTFIELDS, $post_data);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

print "Submitting FaceAuthentication task for $gallery and $probe1\n";
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
print 'Waiting for FaceAuthentication task with JobId: '.$job_id."\n";

// Now lets wait until the job is done, by asking every 0.5 seconds.....
$ch2 = curl_init();
curl_setopt($ch2, CURLOPT_USERPWD, $videoai['apiKey_id'] . ":" . $videoai['apiKey_secret']);
curl_setopt($ch2, CURLOPT_URL, $service.'/'.$job_id);
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
$score= $task['score'];
$authenticated = $task['authenticated'];

if($authenticated) {
    print "Faces matched with score $score\n";
} else {
    print "Faces not matched with score $score\n";
}
?>