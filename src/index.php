<?php

$dbh = new PDO ( "mysql:host=mysql_db; dbname=test", "root", 'wp' );
$dbh->exec("SET CHARACTER SET utf8");

$sql = "SELECT * FROM test";

error_log($sql);

$query = $dbh->prepare ($sql);
$query->execute ();

$results = $query->fetchAll(PDO::FETCH_ASSOC);
$json = json_encode($results);

echo $json;