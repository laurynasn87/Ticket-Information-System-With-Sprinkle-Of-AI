import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TicketCreationModalComponent } from './ticket-creation-modal.component';

describe('TicketCreationModalComponent', () => {
  let component: TicketCreationModalComponent;
  let fixture: ComponentFixture<TicketCreationModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TicketCreationModalComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TicketCreationModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
