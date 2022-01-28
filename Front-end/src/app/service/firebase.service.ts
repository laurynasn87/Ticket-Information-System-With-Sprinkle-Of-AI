import { Injectable, NgZone } from '@angular/core';
import {AngularFireAuth} from '@angular/fire/auth'
import { Router } from "@angular/router";
import { AngularFirestore, AngularFirestoreDocument } from '@angular/fire/firestore';
import { ConfigService } from './Config/config.service';

@Injectable({
  providedIn: 'root'
})
export class FirebaseService {
  userData: any;
  constructor(
    public afs: AngularFirestore,
    public firebaseAuth : AngularFireAuth,
    private Cfs: ConfigService,
    public router: Router,
    public ngZone: NgZone
    ) {    
      this.firebaseAuth.idToken.subscribe(res =>{
        localStorage.setItem('bearer', JSON.stringify(res));
      })

      this.firebaseAuth.authState.subscribe(async user => {
        if (user) {
          await this.MergeWithDatabaseUserData(user).then((res)=>{this.userData = res})
          localStorage.setItem('user', JSON.stringify(this.userData));
          this.SetUserData(this.userData)
        } else {
          localStorage.setItem('user','{}');
        }
      })
      this.firebaseAuth.auth.onIdTokenChanged(res => {
        res?.getIdToken().then(res=>{
          localStorage.setItem('bearer', JSON.stringify(res))
          this.Cfs.GetAllConfigs()
        }   );
      })
    }
  
  // Sign in with email/password
  SignIn(email: string, password: string) {
    return this.firebaseAuth.auth.signInWithEmailAndPassword(email, password)
    .then(async (result: { user: any; }) => {
      await new Promise(r => setTimeout(r, 1200));
      this.ngZone.run(() => {
        this.router.navigate(['home']);
      })
      this.Cfs.GetAllConfigs()
      return "";
    }).catch((error: { message: any; }) => {
      return error.message
    })
  }
  get isLoggedIn(): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (user !== null && user.uid !== undefined) ? true : false;
  }
  get isAdmin(): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (this.isLoggedIn && user.role !== undefined && user.role == "Admin") ? true : false;
  }
  get isRequester(): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (this.isLoggedIn && user.role !== undefined && user.role == "Requester") ? true : false;
  }
  get isOrgRequested(): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (this.isLoggedIn && user.role !== undefined && user.organization != 0) ? true : false;
  }
  get isUserLinked(): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (user !== null && user.userId !== undefined && user.userId !== 0) ? true : false;
  }
  isCurrUser(uid:string): boolean {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return (user !== null && user.uid == uid) ? true : false;
  }
  get GetUserLinkedId(): number {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return user.userId;
  }
  get GetUserName(): number {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return user.displayName;
  }
  get GetUserOrganization(): number {
    const user = JSON.parse(localStorage.getItem('user')|| '{}');
    return user.organization;
  }

  // Reset Forggot password
  ForgotPassword(passwordResetEmail: any) {
    return this.firebaseAuth.auth.sendPasswordResetEmail(passwordResetEmail)
    .catch((error) => {
      console.log(error)
    })
  }
  FirebaseService(provider: any) {
    return this.firebaseAuth.auth.signInWithPopup(provider)
    .then((result: { user: any; }) => {
       this.ngZone.run(() => {
          this.router.navigate(['home']);
        })
      this.SetUserData(result.user);
    }).catch((error: any) => {
      window.alert(error)
    })
  }

  /* Setting up user data when sign in with username/password, 
  sign up with username/password and sign in with social auth  
  provider in Firestore database using AngularFirestore + AngularFirestoreDocument service */
  SetUserData(user: { uid: any; email: any; displayName: any; role: any, userId: any, organization:any }) {
    const userRef: AngularFirestoreDocument<any> = this.afs.doc(`users/${user.uid}`);
    let userData = {
        uid: user.uid,
        email: user.email,
        displayName: user?.displayName,
        userId: user?.userId,
        organization:user?.organization,
        role:user?.role}

      return userRef.set(userData, {
        merge: true
    } );
  }
  async GetUserDatabaseData(uid: any)
  {
    let databaseUser: any ={}
    await this.afs.firestore.collection('users').doc(uid).get().then((usr) => {
      if (usr.exists){
        databaseUser = usr.data()
      }
    }).catch((error) => {
      console.log("Error getting database user document:", error);
  })
    return databaseUser;
  }
  async MergeWithDatabaseUserData(FireAuthUserData:any,DatabaseUserData:any = null){
   let NewMergedUser : any = {}
   NewMergedUser["uid"] = FireAuthUserData.uid
   NewMergedUser["email"] = FireAuthUserData.email
  if (DatabaseUserData == null){
    await this.GetUserDatabaseData(FireAuthUserData.uid).then((res)=> DatabaseUserData = res)
    }

  if (DatabaseUserData != undefined && DatabaseUserData != {}){
    NewMergedUser["role"] = DatabaseUserData["role"]
    NewMergedUser["displayName"] = DatabaseUserData["displayName"]
    NewMergedUser["organization"] = DatabaseUserData["organization"]
    NewMergedUser["userId"] = DatabaseUserData["userId"]
  }

return NewMergedUser
}
  // Sign out 
  SignOut() {
    return this.firebaseAuth.auth.signOut().then(() => {
      localStorage.removeItem('user');
      this.router.navigate(['sign-in']);
    })
  }


}
