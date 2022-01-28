import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';
import { FirebaseService } from 'src/app/service/firebase.service';
declare var $: any;
@Component({
  selector: 'app-personal-tickets',
  templateUrl: './personal-tickets.component.html',
  styleUrls: ['./personal-tickets.component.scss']
})
export class PersonalTicketsComponent implements OnInit {

  CurrMode = "Loading..."
  Columns_Config: any = []
  Filters_Config: any = []
  UserId: number = 0;
  TicketCount = 0
  AllTickets: any = []
  Data = [{ ticketStatus: "", data: [] }]
  show_bar = true
  constructor(public router: Router, private apiService: ApiService, private configService: ConfigService, public authSvc: FirebaseService) { }

  ngOnInit(): void {
    this.UserId = this.authSvc.GetUserLinkedId
    this.initConfigs(this.GetTickets)
    
  }

  initConfigs(DataInitFunction: any) {
    
      let conf: any = this.configService.GetSavedConfig("My_Tickets_filters")
      this.Filters_Config = JSON.parse(conf.Value)
      this.CurrMode = this.Filters_Config[0].name

      let columns: any = this.configService.GetSavedConfig("MyTickets_Collumns")
      let tempColumns = JSON.parse(columns.Value)
      let isReq = this.authSvc.isRequester
      for (let i =0; i<tempColumns.length; i++)
      {
        if (tempColumns[i].type == "Requester" && isReq)
            this.Columns_Config.push(tempColumns[i])
        if (tempColumns[i].type == "User" && !isReq)
            this.Columns_Config.push(tempColumns[i])
        if (tempColumns[i].type == undefined)
            this.Columns_Config.push(tempColumns[i])
      }
      DataInitFunction(this)
  }
  GetTickets(instance = this) {
    let filterField = "assignee_id"
    if (instance.authSvc.isRequester)
    filterField = "requester_id"
    instance.apiService.Get("Tickets?page=0&additionalfilters="+filterField+".id:" + instance.UserId + ";").subscribe(res => {
      var response: any = res
      instance.initTable(response)
    })
  }
  initTable(Data: any) {
    if (Data.length == 0)
    {
      this.show_bar = false
      return
    }

    let temp = [{ ticketStatus: this.GetDataProperty("Ticket Status.value", Data[0]), data: [Data[0]] }]
    for (let i = 1; i < Data.length; i++) {
      let existing = temp.find(x => x.ticketStatus == this.GetDataProperty("Ticket Status.value", Data[i]));
      if (existing != undefined) {
        let indx = temp.findIndex((x) => x.ticketStatus == this.GetDataProperty("Ticket Status.value", Data[i]));
        temp[indx].data.push(Data[i])
      }
      else {
        temp.push({ ticketStatus: this.GetDataProperty("Ticket Status.value", Data[i]), data: [Data[i]] })
      }


    }
    this.AllTickets = temp.sort((a, b) => (a.ticketStatus > b.ticketStatus) ? 1 : ((b.ticketStatus > a.ticketStatus) ? -1 : 0))
    this.SelectResults()

  }
  SelectResults() {
    this.TicketCount = 0
    $.extend(true, this.Data, this.AllTickets)
    let currFilter = this.Filters_Config.find((x: { name: string; }) => x.name == this.CurrMode)?.filters;
    if (currFilter  == undefined)
    return
    for (let i = 0; i < this.AllTickets.length; i++) {
      for (let j = 0; j < currFilter.length; j++) {
        let operator: string = currFilter[j].Operator
        let value: string = currFilter[j].Value
        let temp: never[] = []
        for (let k = 0; k < this.Data[i].data.length; k++) {
          let fieldValue = this.GetDataProperty(currFilter[j].Field, this.Data[i].data[k])
          if (this.Eval_Condition(fieldValue,value,operator))
          {
            temp.push(this.Data[i].data[k])
            this.TicketCount ++
          }
            
        }
        this.Data[i].data = temp;
      }
    }
    this.show_bar = false
  }
  Eval_Condition(A:any,B:any,Operator:any)
  {
    switch(Operator)
    {
      case "==":
      return A == B
      break;
      case "!=":
        return A != B
      break;
      case ">":
        return A > B
        break;
      case "<":
        return A < B
      break;
      default:
        return false

    }
  }
  GetDataProperty(propertyName: string, row: any) {
    let result = ''
    if (!row || !propertyName)
      return ""
    if (propertyName.includes("."))
      result = this.GetDataProperty(propertyName.split('.')[1], row[propertyName.split('.')[0]])
    else
      result = row.hasOwnProperty(propertyName) ? row[propertyName] : " "
    if (typeof result === 'string' && result.includes('_'))
      result = this.replaceAll(result, "_", " ")
    if (Array.isArray(result))
      result = result.join(', ')


    if (this.isDate(result))
      result = new Date(result).toISOString().split("T")[0];

    return result
  }
  isDate(_date: string) {
    const _regExp = new RegExp('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?$');
    return _regExp.test(_date);
  }
  replaceAll(str: string, find: string, replace: string) {
    return str.replace(new RegExp(find, 'g'), replace);
  }
}
