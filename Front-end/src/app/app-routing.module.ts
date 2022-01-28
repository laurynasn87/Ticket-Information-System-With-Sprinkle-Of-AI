import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SignInComponent } from './components/sign-in/sign-in.component';
import { HomeComponent } from './components/home/home.component';
import { AuthGuard } from './service/guard/auth.guard';
import { RoleAuthGuard } from './service/roleGuard/roleAuth.guard';
import { TicketDashboardComponent } from './components/ticket-dashboard/ticket-dashboard.component';
import { UserDashboardComponent } from './components/user-dashboard/user-dashboard.component';
import { OrganizationDashboardComponent } from './components/organization-dashboard/organization-dashboard.component';
import { StatisticsComponent } from './components/statistics/statistics.component';
import { PageNotFoundComponent } from './components/page-not-found/page-not-found.component';
import { SearchDashboardComponent } from './components/search-dashboard/search-dashboard.component';
import { AdminPanelComponent } from './components/admin-panel/admin-panel.component';
import { PersonalTicketsComponent } from './components/personal-tickets/personal-tickets.component';
const routes: Routes = [  
{ path: '', redirectTo: '/sign-in', pathMatch: 'full' },
{ path: 'sign-in', component: SignInComponent },
{ path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
{ path: 'Search', component: SearchDashboardComponent, canActivate: [AuthGuard] },
{ path: 'Ticket/:id', component: TicketDashboardComponent, canActivate: [AuthGuard] },
{ path: 'User/:id', component: UserDashboardComponent, canActivate: [AuthGuard] },
{ path: 'Organization/:id', component: OrganizationDashboardComponent, canActivate: [AuthGuard] },
{ path: 'Statistics', component: StatisticsComponent, canActivate: [AuthGuard] },
{ path: 'MyTickets', component: PersonalTicketsComponent, canActivate: [AuthGuard] },
{ path: 'Admin', component: AdminPanelComponent, canActivate: [RoleAuthGuard] },
{ path: '**', component: PageNotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
