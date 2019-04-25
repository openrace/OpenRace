import { TestBed } from '@angular/core/testing';

import { LedStripCategoriesService } from './led-strip-categories.service';

describe('LedStripCategoriesService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: LedStripCategoriesService = TestBed.get(LedStripCategoriesService);
    expect(service).toBeTruthy();
  });
});
