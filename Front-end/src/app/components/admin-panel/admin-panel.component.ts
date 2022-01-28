import { ThrowStmt } from '@angular/compiler';
import { Component,  Output, OnInit, ViewChild } from '@angular/core';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { ApiService } from 'src/app/service/Api.service';
import { ConfigService } from 'src/app/service/Config/config.service';
import { FirebaseService } from 'src/app/service/firebase.service';
import { environment } from 'src/environments/environment';

declare var $: any;
@Component({
  selector: 'app-admin-panel',
  templateUrl: './admin-panel.component.html',
  styleUrls: ['./admin-panel.component.scss']
})
export class AdminPanelComponent implements OnInit {

  ConfigSelectedValue = "" as string;
  ConfigTextAreaValue = "" as string;
  PageConfig = [] as any
  Configs = [] as any
  SystemUsers = [] as any
  Users = [] as any
  Organizations = [] as any
  NewUser = {uid: "",Email:"",DisplayName:"",Password:"",Role:"",AssociatedUser:"--", Organization:"--"}
  Settings = {UpdateFromZendesk: true, mode:"hdp",Topics_Count:2, Allow_Comments:true} as any
  loading = true;
  show_bar = false
  New_User_Form = true
  LockOrgField = false
  constructor(public router: Router,private apiService: ApiService,private _snackBar: MatSnackBar,public authService: FirebaseService, private configService:ConfigService) {
    
   }

  ngOnInit(): void {
    this.loading=true
    this.initConfigs(this.GetUserData)

  }
  ngAfterViewInit() {
  }
  initConfigs(DataInitFunction: any)
  {
    this.configService.GetConfig("Admin_Page").subscribe(res=>{
      this.PageConfig = res
      if (Array.isArray(this.PageConfig))
      this.PageConfig = this.PageConfig[0];

      this.PageConfig = this.PageConfig.Value
      this.PageConfig = JSON.parse(this.PageConfig)
      this.PageConfig = this.PageConfig.SystemUserDataColumns
      DataInitFunction(this)
    },
    err=>{ console.log("Failed to load configs")
    console.log(err)})
  }
  GetUserData(instance = this)
  {
    instance.loadSettings()
    instance.loadUsers()
  }  
  loadUsers()
  {
    this.apiService.Get("SystemAccounts").subscribe(res=>{
      var response: any = res
      this.SystemUsers = response
      this.loading = false
    })
    this.apiService.Get("Users?page=0").subscribe(res=>{
      var response: any = res
      this.Users=response
      this.Users = this.Users.sort((a:any,b:any) => (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0))
      
    })
    this.apiService.Get("Organizations?page=0").subscribe(res=>{
      var response: any = res
      this.Organizations=response
      this.Organizations = this.Organizations.sort((a:any,b:any) => (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0))
      
    })
  }
  loadSettings()
  {
    this.apiService.Get("Settings").subscribe(res=>{
      var response: any = res
      this.Configs = response
      this.Settings["UpdateFromZendesk"] = (this.Configs.find((x: { Name: string; }) => x.Name === 'UpdateFromZendesk').Value === 'true' ||
      this.Configs.find((x: { Name: string; }) => x.Name === 'UpdateFromZendesk').Value == true)
      this.Settings["Allow_Comments"] = (this.Configs.find((x: { Name: string; }) => x.Name === 'Allow_Comments').Value === 'true'||
      this.Configs.find((x: { Name: string; }) => x.Name === 'Allow_Comments').Value == true)
      this.Settings.mode = this.Configs.find((x: { Name: string; }) => x.Name === 'mode').Value
      this.Settings["Topics_Count"] = this.Configs.find((x: { Name: string; }) => x.Name === 'Topics_Count').Value
    })

  }
  handleSettings(settingName:string)
  {
    
     let value = ""
     switch(settingName)
     {
       case "mode":
        value =  this.Settings.mode;
       break;
       case "UpdateFromZendesk":
        value =  this.Settings.UpdateFromZendesk;
        break;
        case "Allow_Comments":
          value =  this.Settings.Allow_Comments;
        break;
       case "Topics_Count":
        value =  this.Settings.Topics_Count;
        break;
     }
     this.show_bar=true
     this.apiService.Put("Settings",{Name:settingName, Value:value}).subscribe(res=>{
      this.openSnackBar("","Setting has been updated")
      
    }, err =>{
      this.openSnackBar("error","There has been an error when updating")
      this.show_bar=false
      
    }, ()=>{this.show_bar=false
      this.configService.GetNewConfigs()})
  }
  ButtonSetting(url:string, goodResponse = "Data update initiated")
  {
    this.apiService.Get(url).subscribe(res=>{
      this.openSnackBar("",goodResponse)
    }, err =>{
      this.openSnackBar("error",err.message)
    })
    
  }
  configChange(evnt: any)
  {
    let SelectedValue = this.Configs.find((x: { Name: any; }) => x.Name === evnt.value);
    this.ConfigTextAreaValue = SelectedValue.Value
  }
  saveConfig()
  {
    this.show_bar=true
    let ConfigName = this.ConfigSelectedValue
    let ConfigValue:any = this.ConfigTextAreaValue
    let OldValue = this.Configs.find((x: { Name: any; }) => x.Name === ConfigName);

    if (ConfigName != "" && ConfigValue != OldValue)
    {
      if (!isNaN(ConfigValue))
      {
        ConfigValue = parseInt(ConfigValue)

      }
      this.apiService.Put("Settings",{Name:ConfigName,Value:ConfigValue}).subscribe(res=>{
        this.openSnackBar("","Config was updated")
        this.loadSettings()
    },err => {
      console.warn('HTTP Error', err)
      this.openSnackBar("error","There has been an error")
      this.show_bar=false
    },()=>{this.show_bar=false;
      this.configService.GetNewConfigs()})
    }
    

  }
  openSnackBar(type: any,message: any) {
    let extraClasses = []
    if (type == 'error') {
      extraClasses = ['red-snackbar'];
    } else {
      extraClasses = ['green-snackbar'];
  }
    this._snackBar.open(message, '', {
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: extraClasses,
      duration: 2000
    });

  }
  showModal() {
    $("#CreationModal").modal('show');
    $('#CreationModal').modal({backdrop: 'static', keyboard: false})  
  }
  closeModal()
  {
    this.NewUser = {uid: "",Email:"",DisplayName:"",Password:"",Role:"",AssociatedUser:"--",Organization:"--"}
    $("#CreationModal").modal('hide');
  }
  resetPassword(email:string)
  {
    if (email.trim() != "")
    {
      this.authService.ForgotPassword(email).then(()=>{
        this.openSnackBar("","Password reset link has been sent")
      }).catch((err) => {
        this.openSnackBar("error","There has been an error")
        console.log(err)
      })
    }
  }
  GetDataProperty(propertyName: string, row: any, propertyType = "text")
  {
    let result: any = ''
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
            

    if (this.isDate(result) || propertyType == "date"){
      if (typeof result === 'string' && result.trim() != "")
        result = parseInt(result)

        if (result != "" && result.toString().trim() != "")
          result = new Date(result).toISOString().split("T")[0];
    }
        
    return result
}
isDate(_date: string){
  const _regExp  = new RegExp('^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(.[0-9]+)?(Z)?$');
  return _regExp.test(_date);
}
replaceAll(str:string, find:string, replace:string) {
  return str.replace(new RegExp(find, 'g'), replace);
}
CreateUser()
  {
    if (this.NewUser != null && this.NewUser.Email !='' && this.NewUser.Password != '' && this.NewUser.DisplayName != '' && this.NewUser.Role !=''){
      this.show_bar=true
      let user = this.Users.find((x: { name: string; }) => x.name == this.NewUser.AssociatedUser)
      let orgid = this.Organizations.find((x: { name: string; }) => x.name.trim() == this.NewUser.Organization)
      let userid =0
      if (user != null)
        userid = user.id
      this.apiService.Post("SystemAccounts",{email: this.NewUser.Email,password: this.NewUser.Password, role: this.NewUser.Role, displayName: this.NewUser.DisplayName, organization:orgid["id"], userid:userid}).subscribe(res=>{
        this.openSnackBar("","User has been created")
        this.loadUsers()
      },err => {
        this.openSnackBar("error","Error:" + err.message)
        this.show_bar=false
      },()=>{this.show_bar=false;
        })
        this.closeModal()
    }
  }
  EditUserModal(user: any)
  {
    this.New_User_Form = false
    this.NewUser.DisplayName = user.displayName;
    this.NewUser.Email = user.email;
    this.NewUser.Role = user.role;
    this.NewUser.uid = user.localId
    let fullUser = this.Users.find((x: { id: number; }) => x.id == user.userId)
    if (fullUser != undefined)
    {
      this.NewUser.AssociatedUser = fullUser.name
    }
    let orgid = this.Organizations.find((x: { id: number; }) => x.id == user.organization)
    if (orgid != undefined)
    {
      this.NewUser.Organization = orgid.name
    }
    this.showModal()
  }
  CreateUserModal()
  {
    this.New_User_Form = true
    this.showModal()
  }
  AssignOrg(evnt:any)
  {
    let user = this.Users.find((x: { name: string; }) => x.name == this.NewUser.AssociatedUser)
    if (user != undefined)
    {
    let orgid = this.Organizations.find((x: { id: number; }) => x.id == user.organization_id?.id)
    if (orgid != undefined)
    {
      this.NewUser.Organization = orgid.name
      this.LockOrgField = true
    }
    else
    {
      this.NewUser.Organization = "--"
      this.LockOrgField = false
    }
  }
  else
  {
    this.NewUser.Organization = "--"
    this.LockOrgField = false
  }
  }
  EditUser()
  {
    if (this.NewUser != null && this.NewUser.Email !='' && this.NewUser.DisplayName != '' && this.NewUser.Role !='' && this.NewUser.uid != ''){
      this.show_bar=true
      let user = this.Users.find((x: { name: string; }) => x.name == this.NewUser.AssociatedUser)
      let userid =0
      if (user != null)
        userid = user.id
      let orgid = this.Organizations.find((x: { name: string; }) => x.name == this.NewUser.Organization)
      if (orgid != undefined)
      {
        orgid = orgid["id"]
      }
      else
      {
        orgid=0
      }
      this.apiService.Post("SystemAccounts/" + this.NewUser.uid ,{ role: this.NewUser.Role, displayName: this.NewUser.DisplayName, userid:userid,organization:orgid}).subscribe(res=>{
        this.openSnackBar("","User has been updated")
        this.loadUsers()
      },err => {
        console.warn('HTTP Error', err)
        this.openSnackBar("error","Error:" + err.message)
        this.show_bar=false
      },()=>{this.show_bar=false;
        console.log(this.authService.isCurrUser(this.NewUser.uid))
       if (this.authService.isCurrUser(this.NewUser.uid))
       {
        window.location.reload();
       }
       this.closeModal()
       this.apiService.Get("SystemAccounts").subscribe(res=>{
        var response: any = res
        this.SystemUsers = response
        this.loading = false
      })})
    }
  }
  DisableUser(uid: any)
  {
    if (uid){
      this.show_bar = true
      this.apiService.Put(`SystemAccounts/DisableUser/${uid}`).subscribe(res=>{
      this.openSnackBar("","User has been disabled")
      this.loadUsers()
  },err => {
    console.warn('HTTP Error', err)
    this.openSnackBar("error","There has been an error")
  },()=>{this.show_bar=false})}
  }
  DeleteUser(uid: any)
  {
    if (uid){
      this.show_bar = true
      this.apiService.Delete(`SystemAccounts/${uid}`).subscribe(res=>{
        this.openSnackBar("","User has been deleted")
        this.loadUsers()
    },err => {
      console.warn('HTTP Error', err)
      this.openSnackBar("error","There has been an error")
    },()=>{this.show_bar=false})}
  }
  GetUnlinkedUsers()
  {
    let results = []
    for (let i =0 ;i< this.Users.length; i++)
    {
      if (this.SystemUsers.find((x: { userId: any; }) => x.userId === this.Users[i].id) == undefined)
      results.push(this.Users[i])
    }
    return results
  }
  EnableUser(uid: any)
  {
    if (uid){
      this.show_bar = true
      this.apiService.Put(`SystemAccounts/EnableUser/${uid}`).subscribe(res=>{
        this.openSnackBar("","User has been enabled")
        this.loadUsers()
    },err => {
      console.warn('HTTP Error', err)
      this.openSnackBar("error","There has been an error")
    },()=>{this.show_bar=false})}
  }
}


