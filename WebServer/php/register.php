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
$name=mysql_real_escape_string($_POST['usernamesignup']); //This value has to be the same as in the HTML form file
$password=mysql_real_escape_string($_POST['passwordsignup']); //This value has to be the same as in the HTML form file
$email=mysql_real_escape_string($_POST['emailsignup']);
$sql="INSERT INTO users_data (name,email,password) VALUES ('$name','$email','$password')"; /*form_data is the name of the MySQL table where the form data will be saved.
name and email are the respective table fields*/
if (!mysql_query($sql,$con)) {
die('Error: ' . mysql_error()); 
} 
echo "The form data was successfully added to your database."; 
mysql_close($con);
?>