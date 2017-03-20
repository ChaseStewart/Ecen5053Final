<!doctype html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>Users Page</title>
		<!-- Latest compiled and minified CSS -->	
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha/css/bootstrap.min.css">
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha/js/bootstrap.min.js"></script>

	</head>
	<body>
                <!-- connect to sql database to get data -->
		<?php
                        /*data required for sql connection*/
			$host = "localhost";
			$user = "root";
			$db_name= "users_data";
			$con = mysql_connect($host, $user);

			if (!$con) 
			{ 
				die('Could not connect: ' . mysql_error()); 
			} 
                        /*sql query to get data from table*/
			mysql_select_db('users_data'); 
			$sql='SELECT u_d.name,u_d.email,ref.name FROM users_data u_d LEFT JOIN ref_access_table ref ON ref.id = u_d.access';
			$result = mysql_query($sql,$con);
			if(!$result){
				die('could not get data:'.mysql_error());
			}
		?>
                <!-- displaying the result into a table -->
		<div class="container">
			<div class="row" style="margin-top: 20px; margin-bottom: 20px">
				<div class="col-md-4"></div>
				<div class="col-md-4"><h1 class="text-center">Users Page</h1></div>
				<div class="col-md-4"></div>
			</div>
			<div class="row">
				<div class="col-md-1"></div>
				<div class="col-md-10">
					<table class="table table-striped" border="2">
						<thead class="thead-inverse">
							<tr>
								<th>User name</th>
								<th>email</th>
								<th>access</th>
							</tr>
						</thead>
						<tbody>
                                                        <!-- seperate the data from the table based on row number and display-->
							<?php

								while($row= mysql_fetch_array($result,MYSQL_NUM)){
									echo "<tr><td>{$row[0]}</td>
									<td>{$row[1]}</td>
									<td>{$row[2]}</td>
									</tr>\n"; 
								}
							?>
						</tbody>
					</table>
				</div>
				<div class="col-md-1"></div>
			</div>
			<?php mysql_close($con); ?>
		</div>
	</body>
</html>    
