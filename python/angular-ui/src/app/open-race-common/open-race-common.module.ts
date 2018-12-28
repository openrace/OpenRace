import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {IMqttServiceOptions, MqttModule} from "ngx-mqtt";
import {MessageQueueClientService} from "./message-queue-client.service";

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: 'localhost',
  port: 9001,
  path: '/mqtt',
};

@NgModule({
  declarations: [

  ],
  imports: [
    CommonModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS)
  ],
  exports: [

  ]
})

export class OpenRaceCommonModule {
}
