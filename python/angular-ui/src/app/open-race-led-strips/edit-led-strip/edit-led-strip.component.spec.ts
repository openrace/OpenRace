import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { EditLedStripComponent } from './edit-led-strip.component';

describe('EditLedStripComponent', () => {
  let component: EditLedStripComponent;
  let fixture: ComponentFixture<EditLedStripComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EditLedStripComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EditLedStripComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
