import { Component, OnChanges, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';
import { FirebaseService } from 'src/app/service/firebase.service';
@Component({
  selector: 'search-dashboard-dashboard',
  templateUrl: './search-dashboard.component.html',
  styleUrls: ['./search-dashboard.component.scss']
})
export class SearchDashboardComponent implements OnInit, OnChanges {
@ViewChild('searchTerm') SearchTerm: any; 
Filters:any = [];
PageConfig: any =[]
FiltersConfig: any
FiltersExpanded = false;
ShowFilter = false;
limitSelection = false;
dropdownSettings: any = [];
mode: string = "Ticket";
dataColumns: any = [];
data: any = [];
recordsPerPage = 0;
totalRecords = 0;
page = 1;
searchPlaceHolder = "Enter key word or ticket number"
orderField=""
Ascending = true
loading = true
constructor(private fb: FormBuilder,private apiService: ApiService, public router: Router, private configService: ConfigService, public authService: FirebaseService) {}

  ngOnInit() {
    this.dropdownSettings = {
        singleSelection: false,
        idField: 'item_id',
        textField: 'item_text',
        selectAllText: 'Select All',
        unSelectAllText: 'Unselect All',
        itemsShowLimit: 4,
        allowSearchFilter: false
    };
    this.initConfigs(this.GetSearchData)

    
}
initConfigs(DataInitFunction: any)
{
    this.PageConfig =  this.configService.GetSavedConfig("SearchConfig")
    if (Array.isArray(this.PageConfig))
    this.PageConfig = this.PageConfig[0];

    this.PageConfig = this.PageConfig.Value
    this.PageConfig = JSON.parse(this.PageConfig)
    DataInitFunction(this)
}
GetSearchData(instance = this)
{
    instance.initFilters()
    instance.initDataColumns()
    instance.initData()
}
initData() 
{
    let urlEndpoint = this.PageConfig.ApiEndPoints[this.mode];
    if (this.authService.isOrgRequested && this.authService.isRequester)
    {
        this.Filters = []
        urlEndpoint = urlEndpoint + "?page=1&additionalfilters=organization_id.id:"+ this.authService.GetUserOrganization + ";"
    }
        
    this.apiService.Get(urlEndpoint).subscribe(res=>{
        var response: any = res
        this.data = response["results"]
        this.page = response["page"]
        this.recordsPerPage = response["page_size"]
        this.totalRecords = response["total_results"]
        this.loading = false;
    }, err => {
        this.loading = false;
    })
}
initSearch(SearchTerm:string, Page = 1)
{
    this.data = []
    this.loading = true
   let additionalFilters =""
   if (this.authService.isOrgRequested && this.authService.isRequester)
        additionalFilters = additionalFilters + "organization_id.id:"+ this.authService.GetUserOrganization + ";"
   else
        additionalFilters = additionalFilters + this.GetFilters();
    let urlEndpoint = this.PageConfig.ApiEndPoints[this.mode] + `?page=${Page}&filter=${SearchTerm}&orderby=${this.orderField}&asc=${this.Ascending}&additionalfilters=${additionalFilters}`;

    if (urlEndpoint != '')
    {
        this.apiService.Get(urlEndpoint).subscribe(res=>{
            var response: any = res
            this.data = response["results"]
            this.page = response["page"]
            this.recordsPerPage = response["page_size"]
            this.totalRecords = response["total_results"]
            this.loading = false
        })
    }
}
GetFilters()
{
    let FilterTerm = '';
    for (let i = 0; i < this.Filters.length; i++) {
        let filterConf:any
        for (let j = 0; j < this.FiltersConfig.length; j++)
        if (this.FiltersConfig[j].Name == this.Filters[i].Name){
            filterConf = this.FiltersConfig[j]
            break;
        }

        let FieldName = filterConf.FilterField
        FilterTerm = FilterTerm + FieldName +":";
        for (let j = 0; j < this.Filters[i].SelectedItems.length; j++)
        {
            if (this.Filters[i].SelectedItems[j].item_id == "All")
            {
                for (let k = 0; k < filterConf.Data.length; k++)
                {
                    FilterTerm = FilterTerm + filterConf.Data[k].item_id +",";
                }
            }
            else
            {
                FilterTerm = FilterTerm + this.Filters[i].SelectedItems[j].item_id +","
            }
            
        }
        FilterTerm = FilterTerm + ";"
      }

      return FilterTerm;
    
}
initDataColumns()
{
   var config
    switch(this.mode) {  
        case "Ticket": { 
            config = this.PageConfig.Ticket;
           break;
        }
        case "User": { 
            config = this.PageConfig.User;
           break;
        }
        case "Organization": { 
            config = this.PageConfig.Organization;
           break;
        }
     }
     if (config?.DataColumns != undefined && config?.DataColumns.length > 0)
     {
         this.dataColumns = config.DataColumns;
     } 
}
onPageChange(nextPage: any)
{
    this.page = nextPage
    this.initSearch(this.SearchTerm.nativeElement.value,nextPage)
}
initFilters()
{
    this.Filters = [];
    switch(this.mode) {  
        case "Ticket": { 
            this.FiltersConfig = this.PageConfig.Ticket.FilterConfig;
            this.searchPlaceHolder = "Enter key word or ticket number"
           break;
        }
        case "User": { 
            this.FiltersConfig = this.PageConfig.User.FilterConfig;
            this.searchPlaceHolder = "Enter user name"
           break;
        }
        case "Organization":
            {
            this.FiltersConfig = []
            this.searchPlaceHolder = "Enter organization name"
            break;
            }
        default:
        {
            this.FiltersConfig = []
        }
     }
     if (this.FiltersConfig != undefined && this.FiltersConfig.length > 0)
     {
         for (var i =0; i<this.FiltersConfig.length; i++)
         {
             let SelectedItems =  this.FiltersConfig[i].SelectedItems;
             if (SelectedItems == "all")
                  SelectedItems = this.FiltersConfig[i].Data;
          this.Filters.push({Name: this.FiltersConfig[i].Name, Data:this.FiltersConfig[i].Data, Placeholder:this.FiltersConfig[i].PlaceHolder, SelectedItems: SelectedItems})
         }
     }

}
initDropDownOptions(data:Array<any>, dropdownOptions:Array<any>)
{
    if (data.length>0)
    {
        for (let i = 0; i < data.length; i++) {
            dropdownOptions.push({item_id: data[i]?.id, item_text: data[i]?.name})
          }
    }
}

onItemSelect(item: any) {
    this.initSearch(this.SearchTerm.nativeElement.value)
}
onItemDeSelect(item: any) {
    this.initSearch(this.SearchTerm.nativeElement.value)
}
onSelectAll(items: any) {
    this.initSearch(this.SearchTerm.nativeElement.value)
}
toogleShowFilter() {
    this.ShowFilter = !this.ShowFilter;
    this.dropdownSettings = Object.assign({}, this.dropdownSettings, { allowSearchFilter: this.ShowFilter });
}

handleLimitSelection() {
    if (this.limitSelection) {
        this.dropdownSettings = Object.assign({}, this.dropdownSettings, { limitSelection: 2 });
    } else {
        this.dropdownSettings = Object.assign({}, this.dropdownSettings, { limitSelection: null });
    }
}
SearchTypeValueChange(value: any)
{
    
    this.SearchTerm = ''
    let newMode = value.target?.value;
    if (this.mode != newMode)
    {
        this.loading = true
        this.data = []
        this.mode = newMode
        this.initFilters();
        this.initDataColumns();
        this.initData();
    }
}
ngOnChanges()
{
}
setOrderField(fieldName:string)
{
    if (fieldName == this.orderField && !this.Ascending)
    {
        this.orderField = "";
        this.Ascending = true;
    }
    else if(fieldName == this.orderField)
    {
        this.Ascending = false;
    }
    else
    {
        this.orderField = fieldName;
        this.Ascending = true
    }
    this.initSearch(this.SearchTerm.nativeElement.value)
}
GetDataProperty(propertyName: string, row: any, propertyType = "text")
{
    let result = ''
    if (!row || !propertyName)
    return ""
    if (propertyName.includes("."))
       result = this.GetDataProperty(propertyName.split('.')[1],row[propertyName.split('.')[0]])
    else
        result = row[propertyName]
        if (typeof result === 'string' && result.includes('_'))
            result=result.replace('_',' ')

    if (this.isDate(result) || propertyType == "date")
        result = new Date(result).toISOString().split("T")[0];
        
    return result
}
expandSearch(element: any)
{
    this.FiltersExpanded =! this.FiltersExpanded;
}
isDate(_date: string){
    const _regExp  = new RegExp('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?$');
    return _regExp.test(_date);
}
openDashboard(id:any)
{
    switch(this.mode) {  
        case "Ticket": { 
            this.router.navigate(['/Ticket', id])
           break;
        }
        case "User": { 
            this.router.navigate(['/User', id])
           break;
        }
        case "Organization": 
        {
            this.router.navigate(['/Organization', id])
            break;
        }
     }

}
}