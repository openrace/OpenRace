import { Injectable } from '@angular/core';
import {Subscription} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class PilotsService {

  constructor() { }

  activatePilot(id: string) {
    console.log('Activated pilot ' + id);
  }

  deactivatePilot(id: string) {
    console.log('Deactivated pilot ' + id);
  }
}

// console.log('Class loaded');
// this.message = 'test';
// this.subscription = this.mqttService.observe('/OpenRace/status/tracker_voltage').subscribe((message: IMqttMessage) => {
//   console.log('New message');
//   this.message = message.payload.toString();
// });

//
// private subscription: Subscription;
// public message: string;
