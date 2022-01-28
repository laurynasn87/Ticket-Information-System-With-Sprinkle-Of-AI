import { formatDate } from '@angular/common';
import { Component, ElementRef, HostListener, OnInit, QueryList, ViewChildren } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ActivatedRoute, Router } from '@angular/router';
import { fromEvent } from 'rxjs';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';
import { FirebaseService } from 'src/app/service/firebase.service';
declare var $: any;
@Component({
  selector: 'app-ticket-dashboard',
  templateUrl: './ticket-dashboard.component.html',
  styleUrls: ['./ticket-dashboard.component.scss']
})
export class TicketDashboardComponent implements OnInit {
  TicketInfoType = true
  TicketId: any
  Ticket: any
  PageConfig = [] as any
  LeftPane = [] as any
  RightPane = [] as any
  Comments = [] as any
  MostSimilarByMainData = [] as any
  MostSimilarByFullData = [] as any
  MostSimilarWithinOrg = [] as any
  MostExperienceUser = [] as any
  OrganizationName = "Organization"
  AllowComments = false as any
  pageYoffset = 0 as any;
  show_bar = false
  loading = { MainDataAi: true, OrgDataAi: true, MainLoading: true }
  isCommentPublic = true;
  NewCommentContent = "";
  isTicketClosed = true
  isInternalTicket = false
  EditMode = false
  AllUsers: any = []
  
  @ViewChildren("editable") EditableFields: any
  @HostListener('window:popstate', ['$event'])
  onPopState(): void {
    location.reload()
  }
  constructor(public router: Router, private route: ActivatedRoute, private apiService: ApiService, private configService: ConfigService, private _snackBar: MatSnackBar, public authService: FirebaseService) {

  }
  onScroll() {
    this.pageYoffset = document.getElementById('main')?.scrollTop;
  }
  
  ngOnInit() {
    this.TicketId = this.route.snapshot.paramMap.get('id');
    this.initConfigs(this.GetTicketData)
  }
  initConfigs(DataInitFunction: any) {
    
    let temp: any = this.configService.GetSavedConfig("Allow_Comments")
    if (Array.isArray(temp))
      temp = temp[0];
    if (temp != undefined)
    this.AllowComments = temp.Value

    this.PageConfig = this.configService.GetSavedConfig("Ticket_Page")
    if (Array.isArray(this.PageConfig))
      this.PageConfig = this.PageConfig[0];
    if (this.PageConfig != undefined){
      this.PageConfig = JSON.parse(this.PageConfig.Value)
      this.LeftPane = this.PageConfig.LeftPane
      this.RightPane = this.PageConfig.RightPane
    }

    DataInitFunction(this)

  }
  removeTags(str:string) {
    if ((str===null) || (str===''))
        return false;
    else
        str = str.toString();
          
    // Regular expression to identify HTML tags in 
    // the input string. Replacing the identified 
    // HTML tag with a null string.
    return str.replace( /(<([^>]+)>)/ig, '');
} 
  openSnackBar(error: boolean, message: any) {
    let extraClasses: string[] = []
    if (error) {
      extraClasses = ['red-snackbar'];
    }
    if (!error) {
      extraClasses = ['green-snackbar'];
    }
    this._snackBar.open(message, '', {
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: extraClasses,
      duration: 2000
    });

  }
  GetTicketData(instance = this) {
    instance.apiService.Get("Users?page=0").subscribe(res => {
      var response: any = res
      instance.AllUsers = response
      instance.AllUsers = instance.AllUsers.sort((a: any, b: any) => (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0))

    })
    instance.apiService.Get("Tickets/" + instance.TicketId).subscribe(res => {
      var response: any = res
      instance.Ticket = response
      if (response.tags.includes("TIS"))
        instance.isInternalTicket = true
      instance.OrganizationName = instance.Ticket.organization_id.name
      instance.Comments = response.comments;
      if (instance.Comments?.length > 0) {
        instance.Ticket['attachments'] = instance.Comments[0].attachments
        instance.Comments.shift()
      }
      instance.loading.MainLoading = false;
      instance.isTicketClosed = instance.Ticket.status == "closed"

      if (instance.isInternalTicket) {
        for (let i = 0; i < instance.LeftPane.length; i++)
          if (instance.LeftPane[i].Edit == true)
            instance.LeftPane[i]["EditableValue"] = instance.GetDataProperty(instance.LeftPane[i].DataField, instance.Ticket, false)
      }

    }, () => {
      instance.openSnackBar(true, "Failed to load ticket data");
      instance.loading.MainLoading = false;
    })
    if (!instance.authService.isRequester) {
      instance.apiService.Get("TicketAiByOrg/" + instance.TicketId).subscribe(res => {
        var response: any = res
        instance.MostSimilarWithinOrg = instance.adjustResultCount(response.Closest_Main_Data)
        instance.loading.OrgDataAi = false;
      }, () => {
        instance.openSnackBar(true, "Failed to load ticket AI data")
        instance.loading.OrgDataAi = false;
      })

      instance.apiService.Get("TicketAi/" + instance.TicketId).subscribe(res => {
        var response: any = res
        instance.MostSimilarByMainData = instance.adjustResultCount(response.Closest_Main_Data)
        instance.MostSimilarByFullData = instance.adjustResultCount(response.Closest_Full_Data)
        instance.MostExperienceUser = instance.adjustResultCount(response.Most_Experience_User)
        instance.loading.MainDataAi = false;
      }, () => {
        instance.openSnackBar(true, "Failed to load ticket AI data");
        instance.loading.MainDataAi = false;
      })
    }
  }
  SaveFields() {
    let updateQuery = ""
    for (let i = 0; i < this.LeftPane.length; i++) {
      if (this.LeftPane[i].Edit == true) {
        if (this.LeftPane[i].EditableValue != this.GetDataProperty(this.LeftPane[i].DataField, this.Ticket,false)) {
          let dataField = this.LeftPane[i].DataField
          let value = this.LeftPane[i].EditableValue
          if (dataField.includes("."))
            dataField = dataField.split(".")[0];
          if (this.LeftPane[i].SelectList != undefined) {
            if (this.LeftPane[i].SelectList == "Users") {
              value = this.AllUsers.find((user: { name: any; }) => user.name == this.LeftPane[i].EditableValue);
              value = value.id
            }
          }
          if (this.LeftPane[i].EditType == "Array" )
            value = value.replaceAll(',', '||').trim()
          if (dataField != "" && value != "") {
            updateQuery += dataField + "=" + value + ";"
          }


        }
      }
      
    }
    if (updateQuery != "")
    {
      this.show_bar = true
      this.apiService.Post("/Tickets/Update/" + this.TicketId, { data: updateQuery }).subscribe(res => {
        location.reload()
        this.show_bar = false
      }, () => {
        this.openSnackBar(true, "Failed to update")
        this.show_bar = false
      })
    }
  }
  formatDate(date: string) {
    return date.replace('Z', " ").replace('T', ' ')
  }
  GetDataProperty(propertyName: string, row: any, ignore_dash = true) {
    let result = ''
    if (!row || !propertyName)
      return ""
    if (propertyName.includes("."))
      result = this.GetDataProperty(propertyName.split('.')[1], row[propertyName.split('.')[0]])
    else
      result = row.hasOwnProperty(propertyName) ? row[propertyName] : " "

    if (Array.isArray(result))
      result = result.join(', ')
    if (typeof result === 'string' && result.includes('_') && ignore_dash)
      result = this.replaceAll(result, "_", " ")

    if (this.isDate(result))
      result = new Date(result).toISOString().split("T")[0];

    return result
  }
  HandleType(value: any, type: any) {
    switch (type) {
      case 'DateInMinutes':
        value = this.secondsToDhms(value)
        break

    }

    return value
  }
  secondsToDhms(minutes: any, showDays = true, showHours = true, showMinutes = true, showSeconds = true) {
    minutes = Number(minutes);
    var d = Math.floor(minutes / (60 * 24));
    var h = Math.floor(minutes / 60 % 24);
    var m = Math.floor(minutes % 60);
    var s = Math.floor(minutes * 60 % 60);

    var dDisplay = d > 0 && showDays ? d + 'd ' : "";
    var hDisplay = h > 0 && showHours ? h + 'h ' : "";
    var mDisplay = m > 0 && showMinutes ? m + 'm ' : "";
    var sDisplay = s > 0 && showSeconds ? s + 's ' : "";
    return dDisplay + hDisplay + mDisplay + sDisplay;
  }
  adjustResultCount(Results: any) {
    if (Results?.length > this.PageConfig.AiRowCount)
      Results.length = this.PageConfig.AiRowCount
    return Results
  }


  isDate(_date: string) {
    const _regExp = new RegExp('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?$');
    return _regExp.test(_date);
  }
  replaceAll(str: string, find: string, replace: string) {
    return str.replace(new RegExp(find, 'g'), replace);
  }
  setInfoType(newType: boolean) {

    this.TicketInfoType = newType
  }
  updateComments() {

    this.show_bar = true
    this.apiService.Put("Tickets/UpdateComments/" + this.TicketId).subscribe(res => {
      let response: any = res
      this.Comments = response.comments;
      this.openSnackBar(false, "Comments Updated")
    }, () => { this.openSnackBar(true, "Failed to update comments") },
      () => { this.show_bar = false })
  }
  openTicket(id: any) {
    this.router.navigate(['Ticket', id]).then(page => { window.location.reload(); });
  }
  openUser(id: any) {
    this.router.navigate(['User', id]).then(page => { window.location.reload(); });
  }
  showModal() {
    $("#CreationModal").modal('show');
    $('#CreationModal').modal({ backdrop: 'static', keyboard: false })
  }
  closeModal() {
    $("#CreationModal").modal('hide');

  }
  isNewlyCreated() {
    let transformedDate = Date.parse(this.Ticket.created_at);
    let userTimezoneOffset = new Date(this.Ticket.created_at).getTimezoneOffset() * 60000;
    let TimeDiff = Date.now() - (transformedDate - Math.abs(userTimezoneOffset));
    var minutes = Math.floor(TimeDiff / 60000);
    if (minutes > 10)
      return false
    else
      return true
  }
  WriteResponse() {
    let caller = 0
    if (!this.isInternalTicket)
      $("#CreationModal").modal('hide');
    else
      caller = this.authService.GetUserLinkedId
    this.show_bar = true;

    if (this.NewCommentContent != '') {
      this.apiService.Post("Tickets/WriteResponse/" + this.TicketId, { message: this.NewCommentContent, public: this.isCommentPublic, caller: caller, requester: this.authService.isRequester }).subscribe(res => {
        this.openSnackBar(false, "Comment Written")
        this.show_bar = false
      }, () => {
        this.openSnackBar(true, "Failed to write a comment")
        this.show_bar = false
      },
        () => {
          this.NewCommentContent = ""
          this.GetTicketData(this)
        })
    }
  }
  EnableEditMode() {
    this.EditMode = !this.EditMode
  }
  CreationTypeChange(event: any) {
    if (event.index == 0) this.isCommentPublic = true;
    else this.isCommentPublic = false;
  }
  scrollToTop() {
    $('main').animate({ scrollTop: 0 }, 600);
  }
  closeTicket() {
    
    this.show_bar = true
    let today = new Date()
    let dformat = [today.getFullYear(),
      ("0" + (today.getMonth() + 1)).slice(-2),
      today.getDate()].join('-')+'T'+
     [today.getHours(),
      ("0" + (today.getMinutes() + 1)).slice(-2),
      today.getSeconds()].join(':')+'Z';
      let changeString = "status=closed;field.Ticket Status=closed;solved_at="+dformat + ";"
    this.apiService.Post("/Tickets/Update/" + this.TicketId, { data: changeString }).subscribe(res => {
      location.reload()
      this.show_bar = false
    }, () => {
      this.openSnackBar(true, "Failed to close")
      this.show_bar = false
    })

  }
  getSelectList(SelectList: string) {
    let returnList: any[] = []
    switch (SelectList) {
      case "Users":
        for (let i = 0; i < this.AllUsers.length; i++)
          returnList.push(this.AllUsers[i].name)
        break
    }
    return returnList
  }
  deleteTicket() {
    if (confirm("Do you really want to delete this ticket?") == true) {
      this.apiService.Post("/Tickets/Delete/" + this.TicketId, {}).subscribe(res => {
        this.router.navigate(['home']);
        this.show_bar = false
      }, () => {
        this.openSnackBar(true, "Failed to delete")
        this.show_bar = false
      })
    }
  }
}