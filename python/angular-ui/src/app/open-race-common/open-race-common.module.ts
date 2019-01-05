import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IMqttServiceOptions, MqttModule } from 'ngx-mqtt';

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: 'localhost',
  port: 5001,
  path: '/mqtt/',
  username: 'openrace',
  password: 'PASSWORD'
};

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS)
  ],
  exports: []
})

export class OpenRaceCommonModule {
}
