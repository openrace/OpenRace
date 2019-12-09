import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PublishMessageComponent } from './publish-message.component';

describe('PublishMessageComponent', () => {
  let component: PublishMessageComponent;
  let fixture: ComponentFixture<PublishMessageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PublishMessageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PublishMessageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
