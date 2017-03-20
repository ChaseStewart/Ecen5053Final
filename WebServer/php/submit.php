<?php
	$host = "localhost";
	$user = "root";
	$db_name= "users_data";

	$con = mysql_connect($host, $user);

	if (!$con) 
	{ 
		die('Could not connect: ' . mysql_error()); 
	} 

	mysql_select_db("users_data", $con);
	$name=mysql_real_escape_string($_POST['username']); 
	$password=mysql_real_escape_string($_POST['password']); 
	$hash_password = hash("sha256", $password);
	$sql="SELECT * FROM users_data WHERE name='$name'and password='$hash_password'"; /*form_data is the name of the MySQL table where the form data will be saved.
	name and email are the respective table fields*/
	$result=mysql_query($sql);
	$row=mysql_fetch_array($result);
	
	if(empty($row['name']) OR empty($row['password'])) 
	{ 
		die('You are unauthorized:'.mysql_error());
	}
	if (!mysql_query($sql,$con)) {
		die('Error: ' . mysql_error()); 
	}

	# now set the logged-in user
	$sql="INSERT INTO logged_in_users (name ) VALUE ('$name')";
	$result=mysql_query($sql);
	if(!$result){
		die('could not log in:'.mysql_error());
	} 

	
	# Finally, set the arm status
	$sql="INSERT INTO arm_status (arm_state ) VALUE (1)";
	$result=mysql_query($sql);
	if(!$result){
		die('Could not Disarm alarming:'.mysql_error());
	} else {
		header('Location:hubpage.php');
	}
	
	mysql_close($con);
?>
