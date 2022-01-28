
import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ApiService } from '../Api.service';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  Configs: any =[]
  constructor(private apiService: ApiService,private _snackBar: MatSnackBar) { 
    
    let config_temp = JSON.parse(localStorage.getItem('config')|| '{}')
    if (Object.keys(config_temp).length === 0 || config_temp == '{}' || config_temp == undefined)
      this.GetNewConfigs()
    else
    this.Configs = config_temp
    if (!this.isValid())
      this.GetNewConfigs()
  }
  GetNewConfigs()
  {
    this.GetAllConfigs().subscribe(res=>{
      this.Configs = res
      this.Configs.push({"Name":"_ValidTil","Value":this.add_minutes(new Date(), 20).toLocaleString()})
      localStorage.setItem('config', JSON.stringify(this.Configs));
    })
  }
  GetAllConfigs()
  {
    return this.apiService.Get("Settings")

  }
  GetConfigs() {  
    return this.Configs;  
  }  
  GetSavedConfig(name:string)
  {
    return this.Configs.find((x: any) => x?.Name == name);
  }
  GetConfig(name:string)
  {
    return this.apiService.Get(`Settings/${name}`)
  }
  private isValid()
  {
    let valid = this.GetSavedConfig("_ValidTil")
    if (valid != undefined){
      valid = valid.Value
      valid = Date.parse(valid)
      if (valid > new Date())
      return true
    }

    return false
  }
  private add_minutes(dt: Date, minutes: number) {
    return new Date(dt.getTime() + minutes*60000);
}
}
