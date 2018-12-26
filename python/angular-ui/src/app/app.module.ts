import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {
  MatButtonModule,
  MatCardModule, MatDividerModule,
  MatExpansionModule,
  MatFormFieldModule, MatInputModule, MatSelectModule,
  MatTabsModule,
  MatToolbarModule
} from "@angular/material";
import { PilotsComponent } from './pilots/pilots.component';
import {IMqttServiceOptions, MqttModule} from "ngx-mqtt";
import {FlexLayoutModule} from "@angular/flex-layout";
import {DragDropModule} from "@angular/cdk/drag-drop";

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
    FlexLayoutModule,
    MqttModule.forRoot(MQTT_SERVICE_OPTIONS),
    BrowserModule,
    BrowserAnimationsModule,
    MatToolbarModule,
    MatTabsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatExpansionModule,
    MatDividerModule,
    MatButtonModule,
    DragDropModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
