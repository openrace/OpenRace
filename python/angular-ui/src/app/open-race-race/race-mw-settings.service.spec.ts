import { TestBed } from '@angular/core/testing';

import { RaceMwSettingsService } from './race-mw-settings.service';

describe('RaceMwSettingsService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: RaceMwSettingsService = TestBed.get(RaceMwSettingsService);
    expect(service).toBeTruthy();
  });
});
