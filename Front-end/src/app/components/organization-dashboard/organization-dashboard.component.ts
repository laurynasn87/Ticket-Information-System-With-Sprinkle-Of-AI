import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';

@Component({
  selector: 'app-organization-dashboard',
  templateUrl: './organization-dashboard.component.html',
  styleUrls: ['./organization-dashboard.component.scss']
})
export class OrganizationDashboardComponent implements OnInit {
  RightPane = [] as any
  private PageConfig = [] as any;
  private OrganizationId: any
  Organization: any
  Ticket_dataColumns: any = [];
  Ticket_data: any = [];
  User_dataColumns: any = []
  User_data: any = [];
  loading = true
  constructor(public router: Router,private route: ActivatedRoute,private apiService: ApiService, private configService: ConfigService) { }

  ngOnInit(): void {
    this.OrganizationId =  this.route.snapshot.paramMap.get('id');
    this.initConfigs(this.GetOrgData)

  }
  initConfigs(DataInitFunction: any)
  {
      this.PageConfig = this.configService.GetSavedConfig("Organization_Page")
      if (Array.isArray(this.PageConfig))
      this.PageConfig = this.PageConfig[0];

      this.PageConfig = this.PageConfig.Value
      this.PageConfig = JSON.parse(this.PageConfig)
      this.RightPane = this.PageConfig.RightPane
      DataInitFunction(this)
  }
  GetOrgData(instance = this)
  {
    instance.apiService.Get("Organizations/" + instance.OrganizationId).subscribe(res=>{
      var response: any = res
      instance.Organization = response
      instance.initTable()
  })
  }
  initTable()
  {
    this.Ticket_dataColumns = this.PageConfig.TicketDataColumns;
    this.User_dataColumns = this.PageConfig.UserDataColumns;
    this.initData()
  }
  initData() {
    let endpoint = "Tickets"
    let ownerFieldName = "organization_id.id"
    let fullQuery = endpoint + "?page=0&orderby=created_at&asc=false&additionalfilters=" +ownerFieldName +":" + this.OrganizationId + ";"
    this.apiService.Get(fullQuery).subscribe(res=>{
      var response: any = res
      this.Ticket_data = response
  },()=>{},()=>{this.loading = false})
  endpoint = "Users"
  fullQuery = endpoint + "?page=0&additionalfilters=" +ownerFieldName +":" + this.OrganizationId + ";"
  this.apiService.Get(fullQuery).subscribe(res=>{
    var response: any = res
    this.User_data = response
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
        if (Array.isArray(result))
          result = result.join(', ')
            

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
