import { Injectable } from '@angular/core';
import { FirebaseService } from '../firebase.service';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    public authService: FirebaseService,
    public router: Router
  ){}
  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    if(this.authService.isLoggedIn !== true) {
        this.router.navigate(['sign-in'])
    }
    return true;
  }
  canRoleActive(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    if(this.authService.isLoggedIn !== true) {
        this.router.navigate(['sign-in'])
        if(this.authService.isAdmin !== true)
          this.router.navigate(['home'])
    }
    return true;
  }
  
  
}
