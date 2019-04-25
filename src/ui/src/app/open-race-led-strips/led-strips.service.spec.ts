import { TestBed } from '@angular/core/testing';

import { LedStripsService } from './led-strips.service';

describe('LedStripsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: LedStripsService = TestBed.get(LedStripsService);
    expect(service).toBeTruthy();
  });
});
