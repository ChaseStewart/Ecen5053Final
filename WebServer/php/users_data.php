<!doctype html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>database connections</title>
    </head>
    <body>
<?php
     $host = "localhost";
     $user = "root";
     $db_name= "users_data";
     $con = mysql_connect($host, $user);

      if (!$con) 
      { 
      die('Could not connect: ' . mysql_error()); 
      } 
      mysql_select_db('users_data'); 
      $sql='SELECT name,email,access FROM users_data';
      //execute the SQL query and return records
      $result = mysql_query($sql,$con);
      if(!$result){
        die('could not get data:'.mysql_error());
       }
       ?>
       <table border="2" style= "background-color: #84ed86; color: #761a9b; margin: 0 auto;" >
      <thead>
        <tr>
          <th>User name</th>
          <th>email</th>
          <th>access</th>
         </tr>
      </thead>
      <tbody>
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
       <?php mysql_close($con); ?>
       </body>
       </html>    
