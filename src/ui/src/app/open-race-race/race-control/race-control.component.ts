import { Component, OnInit } from '@angular/core';
import { RaceService } from '../race.service';

@Component({
  selector: 'app-race-control',
  templateUrl: './race-control.component.html',
  styleUrls: ['./race-control.component.scss']
})
export class RaceControlComponent implements OnInit {


  constructor(private raceService: RaceService) {
  }

  ngOnInit() {
  }

  startRace() {
    this.raceService.startRace();
  }

  stopRace() {
    this.raceService.stopRace();
  }

}
