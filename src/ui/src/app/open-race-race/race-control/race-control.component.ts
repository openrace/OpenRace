import { Component, OnInit } from '@angular/core';
import { RaceService } from '../race.service';
import { MatDialog } from '@angular/material';
import { RaceSettingsComponent } from '../race-settings/race-settings.component';

@Component({
  selector: 'app-race-control',
  templateUrl: './race-control.component.html',
  styleUrls: ['./race-control.component.scss']
})
export class RaceControlComponent implements OnInit {


  constructor(private raceService: RaceService, private dialog: MatDialog) {
  }

  ngOnInit() {
  }

  openSettings() {
    this.dialog.open(RaceSettingsComponent, {
      width: '600px',
      position: {
        top: '96px',
      }
    });
  }

  startRace() {
    this.raceService.startRace();
  }

  stopRace() {
    this.raceService.stopRace();
  }

}
