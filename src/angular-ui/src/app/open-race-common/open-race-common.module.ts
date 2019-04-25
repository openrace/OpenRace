import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IMqttServiceOptions, MqttModule } from 'ngx-mqtt';
import { WINDOW_PROVIDERS } from './window-provider';

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  connectOnCreate: false
};

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS)
  ],
  exports: [],
  providers: [
    WINDOW_PROVIDERS
  ]
})

export class OpenRaceCommonModule {
}
