<?php
   define('DB_SERVER', 'localhost');
   define('DB_USERNAME', 'root');
   define('DB_PASSWORD', '');
   define('DB_DATABASE', 'adaptengine_db');
   $db = mysqli_connect(DB_SERVER,DB_USERNAME,DB_PASSWORD,DB_DATABASE);

   $pdo = new PDO('mysql:host=localhost; dbname=adaptengine_db', 'root', ''); //127.0.0.1
?>