import { Injectable } from '@angular/core';
import { MqttService } from 'ngx-mqtt';

@Injectable({
  providedIn: 'root'
})
export class MessageQueueClientService {

  constructor(private mqttService: MqttService) {
  }

  publishToTopic(topic: string, message: string) {
    console.log(`Message ${message} send to ${topic}`);
    this.mqttService.publish(topic, message).subscribe();
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
