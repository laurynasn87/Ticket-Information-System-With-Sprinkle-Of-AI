import { Component, OnInit } from '@angular/core';
import { ChartData, ChartOptions, ChartType } from 'chart.js';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';
import { FirebaseService } from 'src/app/service/firebase.service'
declare var $: any;
@Component({
  selector: 'app-statistics',
  templateUrl: './statistics.component.html',
  styleUrls: ['./statistics.component.scss']
})

export class StatisticsComponent implements OnInit {
  AllTickets: any = []
  AllOrgs: any = []
  AllUsers: any = []
  AllAi:any = []
  Charts: any = []
  ChartOptions: ChartOptions = {
    responsive: true,
  };
  Filter = ["Ticket"];
  ChartConfig: any = []
  ChartPlugins = []
  show_bar = true
  constructor(private apiService: ApiService, private configService: ConfigService, public authSvc: FirebaseService) { }

  ngOnInit(): void {
    this.initConfigs(this.GetData)
    // this.Charts.push({Name:"Tickes By Org",ChartType:"Pie",Type:"Organizations",Data:{labels:["Velorm","Rathbones","Sabadell"],datasets:[{data:[100,15,123]}]}})

  }

  initConfigs(DataInitFunction: any) {
    let chartConf: any = this.configService.GetSavedConfig("ChartsConfig")
    this.ChartConfig = JSON.parse(chartConf.Value)
    DataInitFunction(this)
  }
  GetData(instance = this) {
    instance.apiService.Get("Organizations?page=0").subscribe((res: any) => {
      let response = res
      instance.AllOrgs = response
    },()=>{},()=>{
      instance.apiService.Get("Users?page=0").subscribe((res: any) => {
        let response = res
        instance.AllUsers = response
      },()=>{},()=>{
        instance.apiService.Get("TicketAi").subscribe((res: any) => {
          let response = res
          instance.AllAi = response
        },()=>{},()=>{
        instance.apiService.Get("Tickets?page=0").subscribe((res: any) => {
          let response = res
          instance.AllTickets = response
        }, () => { }, () => { instance.initCharts() })
      })
    })
    })
  }
  initCharts() {

    for (let i = 0; i < this.ChartConfig.length; i++) {
      let data: string | any[] = [];
      let Labels: string | any[] = []
      let Values: string | any[] = []
      switch (this.ChartConfig[i].Entity) {
        case "Organization":
          $.extend(true, data, this.AllOrgs);
          break
        case "Ticket":
          $.extend(true, data, this.AllTickets);
          break
        case "User":
          $.extend(true, data, this.AllUsers);
          break
        case "Ai Models":
            $.extend(true, data, this.AllAi);
          break
      }

      for (let j = 0; j < this.ChartConfig[i].Conditions.length; j++) {
        let operator: string = this.ChartConfig[i].Conditions[j].Operator
        let value: string = this.ChartConfig[i].Conditions[j].Value
        if (value.includes("$"))
        {
          value = this.CustomVariable(value)
        }
          
        let temp: any = []
        for (let k = 0; k < data.length; k++) {
          let fieldValue = this.GetDataProperty(this.ChartConfig[i].Conditions[j].Field, data[k])
          if (this.Eval_Condition(fieldValue, value, operator)) {
            temp.push(data[k])
          }

        }
        data = temp;
      }



      for (let l = 0; l < data.length; l++) {
        let indx = Labels.indexOf(this.GetDataProperty(this.ChartConfig[i].NamieField, data[l]))
        if (indx > -1) {
          switch (this.ChartConfig[i].ValueType) {
            case "Sum":
              let value = parseFloat(this.GetDataProperty(this.ChartConfig[i].ValueField, data[l]))
              if (value != undefined)
                Values[indx] += value
              break
            case "Count":
            default:
              Values[indx]++
          }

        }
        else {
          Labels.push(this.GetDataProperty(this.ChartConfig[i].NamieField, data[l]))
          switch (this.ChartConfig[i].ValueType) {
            case "Sum":
              let value = parseFloat(this.GetDataProperty(this.ChartConfig[i].ValueField, data[l]))
              if (value != undefined)
                Values.push(value)
              else
                Values.push(0)
              break
            case "Count":
            default:
              Values.push(1)
          }

        }
      }
      this.Charts.push({ Name: this.ChartConfig[i].Name, Legend:this.ChartConfig[i].Legend, ChartType: this.ChartConfig[i].ChartType, Type: this.ChartConfig[i].Type, Data: { labels: Labels, datasets: [{ data: Values }] } })

    }
    this.initCustomCharts()
    this.show_bar = false
  }
  initCustomCharts()
  {
    var d = new Date();
    d.setMonth(d.getMonth() - 1);
    this.GenerateChart(this.AllTickets.filter((ticket: { updated_at: string; status: string; }) => new Date(ticket.updated_at) > d && ticket.status == "closed"),"organization_id.name","Recently Closed Tickets","pie","Organization")
  }
  CustomVariable(Field: string)
  {
    let returnString = Field
    switch(returnString)
    {
      case "$UserId":
        returnString = this.authSvc.GetUserLinkedId.toString()
    }

    return returnString
  }
  GenerateChart(list: any,FieldName:string,Name:string,ChartType:string,Type:string) {
    let OrgnNames: string | any[] = []
    let OrgValues: string | any[] = []
    for (let i = 0; i < list.length; i++) {
      let indx = OrgnNames.indexOf(this.GetDataProperty(FieldName, list[i]))
      if (indx > -1) {
        OrgValues[indx]++
      }
      else {
        OrgnNames.push(this.GetDataProperty(FieldName, list[i]))
        OrgValues.push(1)
      }
    }
    this.Charts.push({ Name: Name, ChartType: ChartType, Type:Type, Data: { labels: OrgnNames, datasets: [{ data: OrgValues }] } })
  }
  Eval_Condition(A: any, B: any, Operator: any) {
    switch (Operator) {
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
  ShowChart(chart: any) {
    return this.Filter.includes(chart.Type);
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
