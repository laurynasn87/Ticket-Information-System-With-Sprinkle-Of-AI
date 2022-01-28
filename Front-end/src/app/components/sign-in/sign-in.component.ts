import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { analytics } from 'firebase';
import {FirebaseService} from "../../service/firebase.service"
@Component({
  selector: 'app-sign-in',
  templateUrl: './sign-in.component.html',
  styleUrls: ['./sign-in.component.scss']
})
export class SignInComponent implements OnInit {
  ErrorMsg = "Incorrect Credentials!";
  showErrorMsg = false
  loading = false;

  constructor(
    public authService: FirebaseService, public router: Router) {
    if (authService.isLoggedIn) {
      router.navigate(['home']);
    }
   }

  ngOnInit(): void {
  }
  
  login(email: string, password: string)
  {
    this.loading=true;
    if (email && password)
    {
    this.authService.SignIn(email,password).then((res: string) =>{
      if (res !== "")
      {
        this.ErrorMsg = this.sentenceCase(res.replace("_"," ").split(".")[0]).toString()
        this.showErrorMsg = true;
      }
      else
      {
        this.showErrorMsg = false;
        this.router.navigate(['home']);
      }
     }).catch((error: { message: any; }) => {
       console.warn("Error while logging in ", error.message)
    }).finally(() =>{
      this.loading=false;
    });
  }
  else
  {
    this.ErrorMsg = "First, please fill the required fields"
    this.showErrorMsg = true;
    this.loading=false;
  }
  }
   sentenceCase (str: string) {
    if ((str===null) || (str===''))
         return false;
    else
     str = str.toString();
    
   return str.replace(/\w\S*/g, 
  function(txt){return txt.charAt(0).toUpperCase() +
         txt.substr(1).toLowerCase();});
  }
}
