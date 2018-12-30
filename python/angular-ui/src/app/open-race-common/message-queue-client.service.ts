import { Injectable } from '@angular/core';
import { MqttService } from 'ngx-mqtt';
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { QueueMessage } from './queue-message';

@Injectable({
  providedIn: 'root'
})
export class MessageQueueClientService {

  constructor(private mqttService: MqttService) {
  }

  publishToTopic(topic: string, message: string) {
    console.log(`Message ${message} send to ${topic}`);
    this.mqttService.publish(topic, message, {qos: 1, retain: true}).subscribe();
  }

  subscribeToTopic(topic: string): Observable<QueueMessage> {
    return this.mqttService.observe(topic).pipe(map(message => new QueueMessage(message.topic, message.payload.toString())));
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
