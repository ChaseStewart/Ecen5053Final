function validation(){
         // For new user signup, ensure all fields are filled to satisfaction

         // Don't allow empty username
         if( document.myForm.usernamesignup.value == "" )
         {
            alert( "Please provide your name!" );
            document.myForm.usernamesignup.focus() ;
            return false;
         }

         // Don't allow empty email
         if( document.myForm.emailsignup.value == "" )
         {
            alert( "Please provide your Email!" );
            document.myForm.emailsignup.focus() ;
            return false;
         }
        
         // Don't allow empty password
         if( document.myForm.passwordsignup.value == "" )
         {
            alert( "Please provide your password!" );
            document.myForm.passwordsignup.focus() ;
            return false;
         }

         // don't allow empty password-confirm
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

         // ensure email entry has <something>@<something>.<something>
         if (atpos < 1 || ( dotpos - atpos < 2 )) 
         {
            alert("Please enter correct email ID")
            document.myForm.emailsignup.focus() ;
            return false;
         }

        // Don't allow non_matching password and password-confirm
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
