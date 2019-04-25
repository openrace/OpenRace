import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { LedStripsListComponent } from './led-strips-list.component';

describe('LedStripsListComponent', () => {
  let component: LedStripsListComponent;
  let fixture: ComponentFixture<LedStripsListComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ LedStripsListComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(LedStripsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
