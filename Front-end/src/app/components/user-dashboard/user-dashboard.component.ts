import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';

@Component({
  selector: 'app-user-dashboard',
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.scss']
})
export class UserDashboardComponent implements OnInit {
  RightPane = [] as any
  PageConfig = [] as any
  UserId: any
  User: any
  dataColumns: any = [];
  Assigned_Tickets: any = [];
  Requested_Tickets: any = [];
  loading = true
  constructor(public router: Router,private route: ActivatedRoute,private apiService: ApiService, private configService: ConfigService) { }

  ngOnInit(): void {
    this.UserId =  this.route.snapshot.paramMap.get('id');
    this.initConfigs(this.GetUserData)
  }
  initConfigs(DataInitFunction: any)
  {
    
      this.PageConfig = this.configService.GetSavedConfig("User_Page")
      if (Array.isArray(this.PageConfig))
      this.PageConfig = this.PageConfig[0];

      this.PageConfig = this.PageConfig.Value
      this.PageConfig = JSON.parse(this.PageConfig)
      this.RightPane = this.PageConfig.RightPane
      DataInitFunction(this)
  }
  GetUserData(instance = this)
  {
    instance.apiService.Get("Users/" + instance.UserId).subscribe(res=>{
      var response: any = res
      instance.User = response
      instance.RightPane = instance.PageConfig.RightPane
      instance.initTable()
  },()=>{},()=>{instance.loading = false})
  }
  initTable()
  {
    this.dataColumns = this.PageConfig.DataColumns;
    this.initData()
  }
  initData() {
    let endpoint = "Tickets"
    let ownerFieldName = "assignee_id.id"
    let fullQuery = endpoint + "?page=0&additionalfilters=" +ownerFieldName +":" + this.UserId + ";"
    this.apiService.Get(fullQuery).subscribe(res=>{
      var response: any = res
      this.Assigned_Tickets = response
  })
  ownerFieldName = "requester_id.id"
  fullQuery = endpoint + "?page=0&additionalfilters=" +ownerFieldName +":" + this.UserId + ";"
  this.apiService.Get(fullQuery).subscribe(res=>{
    var response: any = res
    this.Requested_Tickets = response
})
  }
  formatDate(date:string)
  {
    return date.replace('Z'," ").replace('T',' ')
  }
  GetDataProperty(propertyName: string, row: any)
  {
    let result = ''
    if (!row || !propertyName)
      return ""
    if (propertyName.includes("."))
       result = this.GetDataProperty(propertyName.split('.')[1],row[propertyName.split('.')[0]])
    else
        result = row.hasOwnProperty(propertyName)?row[propertyName]:" "
        if (typeof result === 'string' && result.includes('_'))
            result=this.replaceAll(result,"_"," ")
            

    if (this.isDate(result))
        result = new Date(result).toISOString().split("T")[0];
        
    return result
}
isDate(_date: string){
  const _regExp  = new RegExp('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?$');
  return _regExp.test(_date);
}
replaceAll(str:string, find:string, replace:string) {
  return str.replace(new RegExp(find, 'g'), replace);
}
}
