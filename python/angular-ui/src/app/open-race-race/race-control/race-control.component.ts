import { Component, Input, OnInit } from '@angular/core';
import { RaceService } from '../race.service';

class RaceSettings {
  amountOfLaps: number;
  startDelayInSeconds: number;
  minLapTimeInSeconds: number;
  raceMw: number;
}

@Component({
  selector: 'app-race-control',
  templateUrl: './race-control.component.html',
  styleUrls: ['./race-control.component.css']
})
export class RaceControlComponent implements OnInit {

  raceMwSettings: number[] = [25, 40, 400];

  private raceSettings: RaceSettings = new RaceSettings();

  constructor(private raceService: RaceService) {
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
