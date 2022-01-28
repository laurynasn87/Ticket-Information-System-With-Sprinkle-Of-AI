import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AngularFireModule } from '@angular/fire'
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { AngularFireAuthModule } from "@angular/fire/auth";
import { environment } from 'src/environments/environment';
import { AngularFirestoreModule } from '@angular/fire/firestore';
import { SignInComponent } from './components/sign-in/sign-in.component';
import { NavBarComponent } from './components/nav-bar/nav-bar.component';
import { SearchDashboardComponent } from './components/search-dashboard/search-dashboard.component';
import { NgMultiSelectDropDownModule } from 'ng-multiselect-dropdown';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { UserDashboardComponent } from './components/user-dashboard/user-dashboard.component';
import { TicketDashboardComponent } from './components/ticket-dashboard/ticket-dashboard.component';
import { OrganizationDashboardComponent } from './components/organization-dashboard/organization-dashboard.component';
import { StatisticsComponent } from './components/statistics/statistics.component';
import {HttpClientModule} from '@angular/common/http'
import { NgxPaginationModule } from 'ngx-pagination';
import { AdminPanelComponent } from './components/admin-panel/admin-panel.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatTabsModule } from '@angular/material/tabs'
import {MatMenuModule} from '@angular/material/menu';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import {MatSelectModule} from '@angular/material/select';
import {MatSnackBarModule} from '@angular/material/snack-bar';
import {MatButtonToggleModule} from '@angular/material/button-toggle';
import { MatButtonModule } from '@angular/material/button';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatProgressBarModule} from '@angular/material/progress-bar';
import { PersonalTicketsComponent } from './components/personal-tickets/personal-tickets.component';
import {MatSidenavModule} from '@angular/material/sidenav';
import { NgChartsModule } from 'ng2-charts';
import {MatStepperModule} from '@angular/material/stepper';
import {MatFormFieldModule} from '@angular/material/form-field'
import {MatInputModule} from '@angular/material/input';
import { TicketCreationModalComponent } from './components/ticket-creation-modal/ticket-creation-modal.component';
@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    SignInComponent,
    NavBarComponent,
    SearchDashboardComponent,
    UserDashboardComponent,
    TicketDashboardComponent,
    OrganizationDashboardComponent,
    StatisticsComponent,
    AdminPanelComponent,
    PageNotFoundComponent,
    PersonalTicketsComponent,
    TicketCreationModalComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    AngularFireModule.initializeApp(environment.firebase),
    AngularFireAuthModule,
    FormsModule,
    ReactiveFormsModule,
    NgMultiSelectDropDownModule.forRoot(),
    AngularFirestoreModule,
    HttpClientModule,
    NgxPaginationModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatMenuModule,
    MatSlideToggleModule,
    MatSelectModule,
    MatSnackBarModule,
    MatButtonToggleModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatSidenavModule,
    NgChartsModule,
    MatStepperModule,
    MatFormFieldModule,
    MatInputModule
  ],
  providers: [AppComponent],
  bootstrap: [AppComponent]
})
export class AppModule { }
