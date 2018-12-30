import { Component, OnInit } from '@angular/core';
import { MatSlideToggleChange } from '@angular/material';
import { PilotsService } from '../pilots.service';
import { Pilot } from '../pilot';

@Component({
  selector: 'app-pilots-list',
  templateUrl: './pilots-list.component.html',
  styleUrls: ['./pilots-list.component.css']
})
export class PilotsListComponent implements OnInit {
  private pilots: Pilot[];

  constructor(private pilotsService: PilotsService) {
    this.pilotsService.pilots.subscribe(newPilots => this.pilots = newPilots);
  }

  ngOnInit() {

  }

  pilotStatusToggled(event: MatSlideToggleChange) {
    if (event.checked) {
      this.pilotsService.activatePilot(event.source.id);
    } else {
      this.pilotsService.deactivatePilot(event.source.id);
    }
  }
}
