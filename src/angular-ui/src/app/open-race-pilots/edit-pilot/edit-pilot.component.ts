import { Component, Input, OnInit } from '@angular/core';
import { PilotsService } from '../pilots.service';
import { Pilot } from '../pilot';

@Component({
  selector: 'app-edit-pilot',
  templateUrl: './edit-pilot.component.html',
  styleUrls: ['./edit-pilot.component.css']
})
export class EditPilotComponent implements OnInit {
  @Input() private pilot: Pilot;

  constructor(private pilotService: PilotsService) {
  }

  ngOnInit() {
  }

  updatePilot() {
    this.pilotService.updatePilot(this.pilot);
  }
}
