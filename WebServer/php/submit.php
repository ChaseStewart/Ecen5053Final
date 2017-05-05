<!--To update the data from the html in the database-->
<?php
        /*data required to connect database*/
	$host    = "localhost";
	$user    = "root";
	$db_name = "users_data";

        /*connect to sql*/
	$con = mysql_connect($host, $user);
	if (!$con) 
	{ 
		die('Could not connect: ' . mysql_error()); 
	} 
        
        /*select database and validate the data from form*/
	mysql_select_db("users_data", $con);

	$name          = mysql_real_escape_string($_POST['username']); 
	$password      = mysql_real_escape_string($_POST['password']); 
	$hash_password = hash("sha256", $password);

	$sql = "SELECT * FROM users_data WHERE name='$name'and password='$hash_password'"; 	
	$result = mysql_query($sql);
	$row    = mysql_fetch_array($result);
	
        /* If no account */
	if(empty($row['name']) OR empty($row['password'])) 
	{ 
		die('You are unauthorized:'.mysql_error());
	}
        
        /*If an error with connection*/
	if (!mysql_query($sql,$con)) {
		die('Error: ' . mysql_error()); 
	}

	 /*now set the logged-in user*/
	$sql    = "INSERT INTO logged_in_users (name ) VALUE ('$name')";
	$result = mysql_query($sql);
	if(!$result){
		die('could not log in:'.mysql_error());
	} 

	
	/*Finally, set the arm status in the arm_status table*/
	$sql    = "INSERT INTO arm_status (arm_state ) VALUE (1)";
	$result = mysql_query($sql);
	if(!$result){
		die('Could not Disarm alarming:'.mysql_error());
	} else {
		header('Location:hubpage.php');
	}
	
	mysql_close($con);
?>
