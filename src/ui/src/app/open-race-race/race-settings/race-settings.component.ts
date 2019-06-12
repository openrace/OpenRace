import { Component, OnInit } from '@angular/core';
import { RaceSettings } from './race.settings';
import { RaceMwSettingsService } from '../race-mw-settings.service';
import { RaceService } from '../race.service';
import { MatDialogRef } from '@angular/material';

@Component({
  selector: 'app-race-settings',
  templateUrl: './race-settings.component.html',
  styleUrls: ['./race-settings.component.scss']
})
export class RaceSettingsComponent implements OnInit {
  raceSettings: RaceSettings = new RaceSettings();
  raceMwSettings: number[];

  constructor(private raceService: RaceService, private raceMwSettingsService: RaceMwSettingsService, private dialogRef: MatDialogRef<RaceSettingsComponent> ) {
    this.raceService.raceSettings.subscribe(next => this.raceSettings = next);
    this.raceMwSettingsService.raceMwSettings.subscribe(next => this.raceMwSettings = next);
  }

  applyRaceSettings() {
    if (this.raceSettings.amountOfLaps !== undefined) {
      this.raceService.setAmountOfLaps(this.raceSettings.amountOfLaps);
    }
    if (this.raceSettings.minLapTimeInSeconds !== undefined) {
      this.raceService.setMinLapTime(this.raceSettings.minLapTimeInSeconds);
    }
    if (this.raceSettings.startDelayInSeconds !== undefined) {
      this.raceService.setStartDelay(this.raceSettings.startDelayInSeconds);
    }
    if (this.raceSettings.raceMw !== undefined) {
      this.raceService.setRaceMw(this.raceSettings.raceMw);
    }

    this.dialogRef.close();
  }

  ngOnInit() {
  }
}
