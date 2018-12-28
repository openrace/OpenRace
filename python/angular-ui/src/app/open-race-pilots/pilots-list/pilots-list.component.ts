import {Component, OnInit} from '@angular/core';
import {MatSlideToggleChange} from "@angular/material";
import {PilotsService} from "../pilots.service";

export class Pilot {
  id: string;
  name: string;
  frequency: string;
  enabled: boolean;
}

const staticpilots: Pilot[] = [
  {id: '1', name: 'Roman', frequency: '433.5', enabled: true},
  {id: '2', name: 'Marc', frequency: '866.3', enabled: false},
  {id: '3', name: 'Claudia', frequency: '866.3', enabled: false},
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
