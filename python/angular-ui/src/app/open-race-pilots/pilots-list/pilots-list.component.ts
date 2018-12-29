import {Component, OnInit} from '@angular/core';
import {MatSlideToggleChange} from "@angular/material";
import {PilotsService} from "../pilots.service";

export class Pilot {
  id: string;
  name: string;
  enabled: boolean;
  band: string;
  channel: string;
  frequency: string;
  gain: number;
}

const staticpilots: Pilot[] = [
  {id: '1', name: 'Roman', band: 'B', channel: '2', frequency: '433.5', gain: 40, enabled: true},
  {id: '2', name: 'Marc', band: 'Fatshark', channel: '3', frequency: '433.5', gain: 40, enabled: true},
  {id: '3', name: 'Claudia', band: 'band a', channel: 'channel a', frequency: '433.5', gain: 40, enabled: true},
];

@Component({
  selector: 'app-pilots-list',
  templateUrl: './pilots-list.component.html',
  styleUrls: ['./pilots-list.component.css']
})
export class PilotsListComponent implements OnInit {
  public pilots: Pilot[] = staticpilots;

  constructor(private pilotsService: PilotsService) {

  }

  ngOnInit() {
  }

  pilotStatusToggled(event: MatSlideToggleChange) {
    if(event.checked) {
      this.pilotsService.activatePilot(event.source.id)
    }
    else {
      this.pilotsService.deactivatePilot(event.source.id)
    }
  }
}
