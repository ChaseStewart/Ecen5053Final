<!--Signup page to add the user details to the database -->
<?php 
        /* details to connect to sql*/
	$host = "localhost";
	$user = "root";
	$db_name= "users_data";

        /*connect to sql*/
	$con = mysql_connect($host, $user);
	if (!$con) 
	{ 
		die('Could not connect: ' . mysql_error()); 
	}

        /*select database and update the table with user data*/
	mysql_select_db("users_data", $con); 

	$name      = mysql_real_escape_string($_POST['usernamesignup']); 
	$password  = mysql_real_escape_string($_POST['passwordsignup']);
	$hash_pass = hash('sha256', $password); 
	$email     = mysql_real_escape_string($_POST['emailsignup']);

        /* to avoid redundancy in user name*/
	$sql    = "SELECT name FROM users_data where name = '$name'";
	$result = mysql_query($sql);
        $row    = mysql_fetch_array($result);

	if(!empty($row['name']))
	{
		die('This user already exists!'.mysql_error());
	}

        /*update the data inyo the table*/
	$sql = "INSERT INTO users_data (name,email,password) VALUES ('$name','$email','$hash_pass')"; 

	if (!mysql_query($sql,$con)) {
		die('Error: ' . mysql_error()); 
	} 

	echo "The form data was successfully added to your database."; 
	mysql_close($con);
?>
