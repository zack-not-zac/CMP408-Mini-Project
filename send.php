<?php
    $city = escapeshellcmd($_GET["cityInput"]);

    $cmd = "python3 ./MQTT_Weather_Publish.py ".$city
    $output = shell_exec($cmd)
    echo $output
?>