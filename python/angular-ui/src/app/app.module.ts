import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { PilotsComponent } from './pilots/pilots.component';
import {IMqttServiceOptions, MqttModule} from "ngx-mqtt";
import {FlexLayoutModule} from "@angular/flex-layout";
import {FormsModule} from "@angular/forms";
import {OpenRacePilotsModule} from "./open-race-pilots/open-race-pilots.module";
import {MaterialModule} from "./material/material.module";

export const MQTT_SERVICE_OPTIONS: IMqttServiceOptions = {
  hostname: '10.5.20.35',
  port: 9001,
  path: '/mqtt',
};


@NgModule({
  declarations: [
    AppComponent,
    PilotsComponent
  ],
  imports: [
    FormsModule,
    FlexLayoutModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS),
    MaterialModule,
    OpenRacePilotsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
