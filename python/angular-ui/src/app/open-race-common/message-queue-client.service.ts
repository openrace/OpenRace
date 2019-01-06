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

  publishToTopicUnretained(topic: string, message: string) {
    console.log(`Message ${message} send to ${topic}`);
    this.mqttService.publish(topic, message, {qos: 1, retain: false}).subscribe();
  }

  subscribeToTopic(topic: string): Observable<QueueMessage> {
    return this.mqttService.observe(topic).pipe(map(message => new QueueMessage(message.topic, message.payload.toString())));
  }
}
