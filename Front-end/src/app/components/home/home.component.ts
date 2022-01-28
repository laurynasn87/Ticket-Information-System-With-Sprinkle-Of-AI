import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { FirebaseService } from '../../service/firebase.service';
@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  Tiles:any = {};
  Linked_User:any = {}
  loading = true;
  constructor(
    public authService: FirebaseService,private apiService: ApiService, public router: Router
  ) { }

  ngOnInit(): void {
    this.InitData()
  }
  InitData()
  {
    let isRequester = this.authService.isRequester
    this.apiService.Put("Tiles",{"userId": this.authService.GetUserLinkedId,"requester":isRequester}).subscribe(res=>{
      var response: any = res
      this.InitTiles(response)
      this.loading = false;
    })
    if (this.authService.GetUserLinkedId != 0 )
    this.apiService.Get("Users/" + this.authService.GetUserLinkedId).subscribe(res=>{
      this.Linked_User = res;
    })
    else
    this.Linked_User = {name:"None"}
  }
  InitTiles(apiResponse: any)
  {
    this.Tiles = apiResponse
  }
  ShortenPriority(priority: string)
  {
    switch(priority) {
      case "low":
        priority = "P4"
        break;
      case "high":
        priority = "P2"
        break;
      case "urgent":
        priority = "P1"
        break;
      case "normal":
        priority = "P3"
        break;
    }
    return priority
  }
  CalculateDateDiff(date:string)
  {
    let returnString = "";
    let transformedDate = Date.parse(date);
    let userTimezoneOffset = new Date().getTimezoneOffset() * 60000;
    let TimeDiff = Date.now() - (transformedDate);
    let formatedDiff = TimeDiff/(1000*60*60*24)
    if (formatedDiff > 365)
      returnString = '+' + Math.floor((formatedDiff / 365)).toString() +'y';
    else if (formatedDiff>=100)
      returnString = Math.floor((formatedDiff / 30)).toString() +'mon';
    else if (formatedDiff > 1)
      returnString = Math.floor(formatedDiff).toString() +'d';
    else
      returnString = Math.floor(formatedDiff * 24).toString() +'h';

      return returnString;
  }


}
