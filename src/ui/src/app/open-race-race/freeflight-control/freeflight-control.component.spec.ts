import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FreeflightControlComponent } from './freeflight-control.component';

describe('FreeflightControlComponent', () => {
  let component: FreeflightControlComponent;
  let fixture: ComponentFixture<FreeflightControlComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FreeflightControlComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FreeflightControlComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
