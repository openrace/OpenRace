import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { FrequencyChooserComponent } from './frequency-chooser.component';

describe('FrequencyChooserComponent', () => {
  let component: FrequencyChooserComponent;
  let fixture: ComponentFixture<FrequencyChooserComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ FrequencyChooserComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(FrequencyChooserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
