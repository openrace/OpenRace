import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { RaceSettingsComponent } from './race-settings.component';

describe('RaceSettingsComponent', () => {
  let component: RaceSettingsComponent;
  let fixture: ComponentFixture<RaceSettingsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ RaceSettingsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(RaceSettingsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
