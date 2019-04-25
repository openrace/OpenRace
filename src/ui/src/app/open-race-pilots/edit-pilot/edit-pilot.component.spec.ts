import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditPilotComponent } from './edit-pilot.component';

describe('EditPilotComponent', () => {
  let component: EditPilotComponent;
  let fixture: ComponentFixture<EditPilotComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditPilotComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditPilotComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
