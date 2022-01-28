import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";  
import { environment } from 'src/environments/environment';
import { FirebaseService } from "./firebase.service";
@Injectable({
    providedIn: 'root'
  })
  export class ApiService
  {

      constructor(private http:HttpClient){

      }
      Get(endpoint:string, Api_Base="")
      {
        let url =  ""
        if (Api_Base == "")
          url = environment.API_BASE
        else
          url = Api_Base
        url = url + endpoint;
        return this.http.get(url,this.headers)
      }
      Put(endpoint:string,Data:any = {})
      {
        let url = environment.API_BASE + endpoint;
        return this.http.put(url,Data,this.headers)
      }
      Post(endpoint:string,Data:any)
      {
        let url = environment.API_BASE + endpoint;
        return this.http.post(url,Data,this.headers) 
      }
      Delete(endpoint:string)
      {
        let url = environment.API_BASE + endpoint;
        return this.http.delete(url,this.headers);
      }

      get headers()
      {
        let key = localStorage.getItem('bearer')
        if (key != null)
          key = JSON.parse(key);
        return {
          headers: new HttpHeaders().set('Authorization', "Bearer " + key )
        }
      }
      
      
  }
