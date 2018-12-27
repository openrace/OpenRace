import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FrequencyChooserComponent} from './frequency-chooser/frequency-chooser.component';
import {MaterialModule} from "../material/material.module";
import {PilotsListComponent} from "./pilots-list/pilots-list.component";
import {FormsModule} from "@angular/forms";
import {IMqttServiceOptions, MqttModule} from "ngx-mqtt";

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: '10.5.20.35',
  port: 9001,
  path: '/mqtt',
};


@NgModule({
  declarations: [
    FrequencyChooserComponent,
    PilotsListComponent],
  imports: [
    CommonModule,
    FormsModule,
    MaterialModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS)
  ],
  exports: [
    PilotsListComponent
  ]
})
export class OpenRacePilotsModule {
}
