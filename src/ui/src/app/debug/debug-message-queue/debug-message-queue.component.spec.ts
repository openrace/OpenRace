import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DebugMessageQueueComponent } from './debug-message-queue.component';

describe('DebugMessageQueueComponent', () => {
  let component: DebugMessageQueueComponent;
  let fixture: ComponentFixture<DebugMessageQueueComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DebugMessageQueueComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DebugMessageQueueComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
