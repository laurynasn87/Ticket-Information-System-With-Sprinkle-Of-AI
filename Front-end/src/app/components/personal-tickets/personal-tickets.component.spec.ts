import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PersonalTicketsComponent } from './personal-tickets.component';

describe('PersonalTicketsComponent', () => {
  let component: PersonalTicketsComponent;
  let fixture: ComponentFixture<PersonalTicketsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PersonalTicketsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(PersonalTicketsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
