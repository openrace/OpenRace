import { Component, OnInit } from '@angular/core';
import {IMqttMessage, MqttService} from "ngx-mqtt";
import {Subscription} from "rxjs";

export class Pilot {
  name: string;
  frequency: string;
  enabled: boolean;
}

const staticpilots: Pilot[] = [
  { name: 'Roman', frequency: '433.5', enabled: true},
  { name: 'Marc', frequency: '866.3', enabled: false},
  { name: 'Claudia', frequency: '866.3', enabled: false},
];

@Component({
  selector: 'app-pilots',
  templateUrl: './pilots.component.html',
  styleUrls: ['./pilots.component.css']
})
export class PilotsComponent implements OnInit {
  public pilots: Pilot[] = staticpilots;

  private subscription: Subscription;
  public message: string;

  constructor(private mqttService: MqttService) {
    console.log('Class loaded');
    this.message = 'test';
    this.subscription = this.mqttService.observe('/OpenRace/status/tracker_voltage').subscribe((message: IMqttMessage) => {
      console.log('New message');
      this.message = message.payload.toString();
    });
  }

  ngOnInit() {
  }

}
