import { Inject, Injectable } from '@angular/core';
import { IMqttServiceOptions, MqttService } from 'ngx-mqtt';
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { QueueMessage } from './queue-message';
import { WINDOW } from './window-provider';

@Injectable({
  providedIn: 'root'
})
export class MessageQueueClientService {

  constructor(@Inject(WINDOW) private window: Window, private mqttService: MqttService) {
    const options: IMqttServiceOptions = {
      hostname: window.location.hostname,
      port: Number(window.location.port),
      path: '/mqtt/'
    };

    this.mqttService.connect(options);

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
