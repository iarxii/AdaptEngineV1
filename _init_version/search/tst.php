<?php

$url = "https://www.google.com/?q=test";
$domain = parse_url($url)['host'];

echo $domain;