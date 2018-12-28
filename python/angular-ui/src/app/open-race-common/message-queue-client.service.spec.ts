import { TestBed } from '@angular/core/testing';

import { MessageQueueClientService } from './message-queue-client.service';

describe('MessageQueueClientService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: MessageQueueClientService = TestBed.get(MessageQueueClientService);
    expect(service).toBeTruthy();
  });
});
