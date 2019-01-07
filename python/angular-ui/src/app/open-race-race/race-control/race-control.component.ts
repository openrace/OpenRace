import { Component, OnInit } from '@angular/core';
import { RaceService } from '../race.service';
import { RaceMwSettingsService } from '../race-mw-settings.service';
import { RaceSettings } from './race.settings';

@Component({
  selector: 'app-race-control',
  templateUrl: './race-control.component.html',
  styleUrls: ['./race-control.component.css']
})
export class RaceControlComponent implements OnInit {

  raceMwSettings: number[];

  private raceSettings: RaceSettings = new RaceSettings();

  constructor(private raceService: RaceService, private raceMwSettingsService: RaceMwSettingsService) {
    this.raceMwSettingsService.raceMwSettings.subscribe(next => this.raceMwSettings = next);
    this.raceService.raceSettings.subscribe(next => this.raceSettings = next);
  }

  ngOnInit() {
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
  }

  startRace() {
    this.raceService.startRace();
  }

  stopRace() {
    this.raceService.stopRace();
  }

}
