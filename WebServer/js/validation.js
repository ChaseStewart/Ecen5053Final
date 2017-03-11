function validation(){
         if( document.myForm.usernamesignup.value == "" )
         {
            alert( "Please provide your name!" );
            document.myForm.usernamesignup.focus() ;
            return false;
         }
         
         if( document.myForm.emailsignup.value == "" )
         {
            alert( "Please provide your Email!" );
            document.myForm.emailsignup.focus() ;
            return false;
         }
         if( document.myForm.passwordsignup.value == "" )
         {
            alert( "Please provide your password!" );
            document.myForm.passwordsignup.focus() ;
            return false;
         }
         if( document.myForm.passwordsignup_confirm.value == "" )
         {
            alert( "Please retype the password!" );
            document.myForm.passwordsignup_confirm.focus() ;
            return false;
         }

         var emailID = document.myForm.emailsignup.value;
         var password = document.myForm.passwordsignup.value;
         var password_c=document.myForm.passwordsignup_confirm.value;
         atpos = emailID.indexOf("@");
         dotpos = emailID.lastIndexOf(".");  
         if (atpos < 1 || ( dotpos - atpos < 2 )) 
         {
            alert("Please enter correct email ID")
            document.myForm.emailsignup.focus() ;
            return false;
         }
        if(password === password_c)
         {
            return(true);
         }
        else{
            alert("Password not matching")
            document.myForm.passwordsignup_confirm.focus() ;
            return false;
            }
         return( true );
}
