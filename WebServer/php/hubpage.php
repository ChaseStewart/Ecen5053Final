<!-- hub landing page-->
<html>
	<head>
		<title>Chase and Mounika Project 2</title>

		<meta charset="utf-8">

		<meta http-equiv="X-UA-Compatible" content="IE=edge">

		<link rel="stylesheet" href="http://s3.amazonaws.com/codecademy-content/courses/ltp/css/bootstrap.css">
		<link rel="stylesheet" href="css/main.css">

	</head>

	<body>

	<div class="nav">
		<div class="container">
			<ul>
				<li class="col-sm-3 text-center"><a href="#">Hubby.io</a></li>
				<li class="col-sm-3 text-center"><a href="set_LEDs.php">Set LEDs</a></li>
				<li class="col-sm-3 text-center"><a onclick="alert('This webpage created by Mounika and Chase for Embedded Interface Design!');">Info</a></li>
				<li class="col-sm-3 text-center"><a href="index.html">Logout</a></li>
			</ul>
		</div>
	</div>
	
	<div class="container">
		<div class="row" style="margin-top: 20px; margin-bottom: 20px">
			<div class="col-md-4"></div>
			<div class="col-md-4"><h1 class="text-center">Main Page</h1></div>
			<div class="col-md-4"></div>
			</div>
		<div class="row">
		<div class="row" style="margin-top: 10px;">
			<div class="col-md-2"></div>
			<!--to connect to the databse and get data to display in the table -->
			<?php
                                /* details to connect to database*/
				$host = "embintdes.cyjeijyfmmbt.us-west-2.rds.amazonaws.com:3306";
				$user = "cstewart";
				$db_name= "users_data";
				$passwd="3mb1ntd3s";

                                /* connect to sql**/
				$con = mysql_connect($host, $user, $passwd);
				if (!$con) 
				{ 
					die('Could not connect: ' . mysql_error()); 
				} 
				/* connect to mysql*/
                                mysql_select_db('users_data'); 
				$sql='SELECT name FROM logged_in_users ORDER BY timestamp DESC limit 1 ';
			
				//execute the SQL query and return records
				$result = mysql_query($sql,$con);
				if(!$result){
					die('could not get data:'.mysql_error());
				}
				while($user= mysql_fetch_array($result,MYSQL_NUM)){
					echo "<div class=\"col-md-8\"><h3 id=\"curr_user\" class=\"text-center\">Current User is {$user[0]} </h3></div>";
				}
			?>
			<div class="col-md-2"></div>
			</div>
		<div class="row">
		<div class="row" style="margin-top: 5px; margin-bottom: 10px">
			<div class="col-md-2"></div>
			<?php
				$sql='SELECT ref.name FROM arm_status a_s LEFT JOIN ref_arm_state ref ON ref.id = a_s.arm_state ORDER BY timestamp DESC limit 1';
			
				//execute the SQL query and return records
				$result = mysql_query($sql,$con);
				if(!$result){
					die('could not get data:'.mysql_error());
				}
				
				while($state= mysql_fetch_array($result,MYSQL_NUM)){
				
					echo "<div class=\"col-md-8\"><h3 id=\"curr_user\" class=\"text-center\">Arm/Disarm Status is {$state[0]} </h3></div>";
				}
			?>

			<div class="col-md-2"></div>
		</div>
		<div class="row" >
			<div class="col-md-4"></div>
			<div class="col-md-6">
				<button class="btn btn-info btn-lg" onclick="window.location='users_data.php'">Users</button><br /><br />
				<button class="btn btn-info btn-lg" onclick="window.location='set_LEDs.php'">LEDs</button><br /><br />
				<!--<button class="btn btn-info btn-lg" onclick="alert('Not yet implemented!');">Music</button><br /><br /> -->
				<!--<button class="btn btn-info btn-lg" onclick="alert('Not yet implemented!');">Stats</button><br /><br /> -->
				<button class="btn btn-info btn-lg" onclick="alert('This webpage created by Mounika and Chase for Embedded Interface Design!');">Info</button><br /><br />
				<button class="btn btn-info btn-lg" onclick="window.location='index.html'">Log Out</button>
			</div>
			<div class="col-md-2"></div>
		</div>
       
	</div>

	</body>
</html>
