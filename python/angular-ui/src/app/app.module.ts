import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {MatCardModule, MatFormFieldModule, MatTabsModule, MatToolbarModule} from "@angular/material";
import { PilotsComponent } from './pilots/pilots.component';
import {IMqttServiceOptions, MqttModule} from "ngx-mqtt";

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
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS),
    BrowserModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatTabsModule,
    MatCardModule,
    MatFormFieldModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
