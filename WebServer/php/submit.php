<?php
$host = "localhost";
$user = "root";
$db_name= "users_data";

$con = mysql_connect($host, $user);

if (!$con) 
{ 
die('Could not connect: ' . mysql_error()); 
} 

mysql_select_db("users_data", $con); //Replace with your MySQL DB Name
$name=mysql_real_escape_string($_POST['username']); //This value has to be the same as in the HTML form file
$password=mysql_real_escape_string($_POST['password']); //This value has to be the same as in the HTML form file
$sql="SELECT *FROM users_data WHERE name='$name'and password='$password'"; /*form_data is the name of the MySQL table where the form data will be saved.
name and email are the respective table fields*/
$result=mysql_query($sql);
$row=mysql_fetch_array($result);
if(!empty($row['name']) AND !empty($row['password'])) 
{ 
header('Location:php/users_data.php');
}
if (!mysql_query($sql,$con)) {
die('Error: ' . mysql_error()); 
} 
mysql_close($con);
?>
