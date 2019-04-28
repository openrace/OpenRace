import { Component, OnInit } from '@angular/core';
import { RaceSettings } from '../race-control/race.settings';
import { RaceService } from '../race.service';
import { RaceMwSettingsService } from '../race-mw-settings.service';

@Component({
  selector: 'app-freeflight-control',
  templateUrl: './freeflight-control.component.html',
  styleUrls: ['./freeflight-control.component.css']
})
export class FreeflightControlComponent implements OnInit {

  raceMwSettings: number[];

  private raceSettings: RaceSettings = new RaceSettings();

  constructor(private raceService: RaceService, private raceMwSettingsService: RaceMwSettingsService) {
    this.raceMwSettingsService.raceMwSettings.subscribe(next => this.raceMwSettings = next);
    this.raceService.raceSettings.subscribe(next => this.raceSettings = next);
  }

  ngOnInit() {
  }

  applySettings() {
    if (this.raceSettings.raceMw !== undefined) {
      this.raceService.setRaceMw(this.raceSettings.raceMw);
    }
  }

  startFreeflight() {
    this.raceService.startFreeflight();
  }

  stopFreeflight() {
    this.raceService.stopRace();
  }

}
