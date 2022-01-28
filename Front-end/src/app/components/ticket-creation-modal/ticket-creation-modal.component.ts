import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatStepper } from '@angular/material/stepper';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiService } from 'src/app/service/Api.service';

@Component({
  selector: 'app-ticket-creation-modal',
  templateUrl: './ticket-creation-modal.component.html',
  styleUrls: ['./ticket-creation-modal.component.scss']
})
export class TicketCreationModalComponent implements OnInit {
  @ViewChild('stepper') stepper: any;
  firstFormGroup: FormGroup | any;
  secondFormGroup: FormGroup | any;
  NewTicket = { Name: "", Description: "", Priority: "", SubType: "", Organization: "", User: "" }
  show_bar=false
  constructor(public activeModal: NgbActiveModal, private _formBuilder: FormBuilder, private apiService: ApiService,private _snackBar: MatSnackBar) { 
    
  }

  ngOnInit(): void {
    
    this.firstFormGroup = this._formBuilder.group({
      firstCtrl: ['', Validators.required],
    });
    this.secondFormGroup = this._formBuilder.group({
      secondCtrl: ['', Validators.required],
    });
    this.ResolveUserFields()
  }
  ResolveUserFields() {
    let usr = JSON.parse(localStorage.getItem('user') || '{}');
    let AssociatedUser = usr.userId
    if (AssociatedUser != 0 && AssociatedUser != "") {
      this.apiService.Get("Users/"+AssociatedUser).subscribe(res => {
        var response: any = res
        AssociatedUser = response
        if (AssociatedUser != undefined) {
          this.NewTicket.User = AssociatedUser.name
        }
      })
    }
    else
    {
      this.NewTicket.User = usr.displayName
    }

      if (usr.organization != undefined || usr.organization != 0)
      this.apiService.Get("Organizations/"+ usr.organization).subscribe(res => {
        var response: any = res
        var orgid:any = response
        if (orgid != undefined)
        {
            this.NewTicket.Organization = orgid.name
        }
      })
}
CreateTicket()
{
  this.show_bar = true
  let usr = JSON.parse(localStorage.getItem('user') || '{}');
  this.apiService.Post("Tickets/Create",{name:this.NewTicket.Name,description:this.NewTicket.Description,priority:this.NewTicket.Priority,subtype:this.NewTicket.SubType,organization:this.NewTicket.Organization,user:this.NewTicket.User,caller:usr.uid}).subscribe(res => {
    var response: any = res
    var url:any = response.url
    if (window != null)
      window.open(url, '_blank')?.focus();
    this.activeModal.dismiss('sucess')
    this._snackBar.open("Ticket Has been created", '', {
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['green-snackbar'],
      duration: 2000
    })
    this.show_bar = false},()=>{
      this._snackBar.open("There has been an error while creating", '', {
        horizontalPosition: 'end',
        verticalPosition: 'top',
        panelClass: ['red-snackbar'],
        duration: 2000
      })
      this.show_bar = false
      //this.activeModal.dismiss('error')
    });
}
goBack(stepper: MatStepper){

  stepper.previous();
}

goForward(stepper: MatStepper){ 
  stepper.next();
}
}
