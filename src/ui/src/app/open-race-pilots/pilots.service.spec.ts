import { TestBed } from '@angular/core/testing';

import { PilotsService } from './pilots.service';

describe('PilotsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: PilotsService = TestBed.get(PilotsService);
    expect(service).toBeTruthy();
  });
});
