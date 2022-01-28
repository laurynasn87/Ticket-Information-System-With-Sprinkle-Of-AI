import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { ModalDismissReasons, NgbModal, NgbModalOptions } from '@ng-bootstrap/ng-bootstrap';
import { FirebaseService } from 'src/app/service/firebase.service';
import { environment } from 'src/environments/environment';
import { TicketCreationModalComponent } from '../ticket-creation-modal/ticket-creation-modal.component';
@Component({
  selector: 'app-nav-bar',
  templateUrl: './nav-bar.component.html',
  styleUrls: ['./nav-bar.component.scss']
})
export class NavBarComponent implements OnInit {
  name = environment.Name
  constructor(public authService: FirebaseService, public router: Router, private modalService: NgbModal) { }

  ngOnInit(): void {
  }
  open() {
    var modalOptions: NgbModalOptions = {
      size:'xl'
    }
    const modalRef = this.modalService.open(TicketCreationModalComponent,modalOptions);
    
  }


}
