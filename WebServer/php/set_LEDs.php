<!doctype html>
<html lang="en">
	<head>
		<meta charset="UTF-8">
		<title>Users Page</title>
		<!-- Latest compiled and minified CSS -->	
		<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
		<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha/css/bootstrap.min.css">
		<link rel="stylesheet" href="css/main.css">
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha/js/bootstrap.min.js"></script>
	</head>
	<body>


		<div class="nav">
			<div class="container">
				<ul>
					<li class="col-sm-3 text-center"><a href="hubpage.php">Hubby.io</a></li>
					<li class="col-sm-3 text-center"><a href="#">Set LEDs</a></li>
					<li class="col-sm-3 text-center"><a onclick="alert('This webpage created by Mounika and Chase for Embedded Interface Design!');">Info</a></li>
					<li class="col-sm-3 text-center"><a href="index.html">Logout</a></li>
				</ul>
			</div>
		</div>

                <!-- displaying the result into a table -->
		<div class="container">
			<div class="row" style="margin-top: 20px; margin-bottom: 20px">
				<div class="col-md-4"></div>
				<div class="col-md-4"><h1 class="text-center">Set LED color</h1></div>
				<div class="col-md-4"></div>
			</div>
			<div class="row">
				<div class="col-md-1"></div>
				<div class="col-md-10">

				<!-- HUGE THANKS to https://bgrins.github.io/spectrum/ for making the color picker possible -->
				<script src='spectrum.js'></script>
				<link rel='stylesheet' href='spectrum.css'/>
				<input id='colorpicker' />

				<script>
					$("#colorpicker").spectrum({
						color: "#f00",
						change: function(color) {
							var resultJSON = JSON.stringify(color.toRgb());
							$.ajax({
								url: 'http://52.34.209.113:8080',
								data: resultJSON,
								dataType: 'json',
								type: 'POST',
								success: function(result){
								$("#div1").html("sent color to Hub");
							}});
						}
					});
				</script>

				</div>
				<div class="col-md-1"></div>
			</div>
		</div>
	</body>
</html>    
