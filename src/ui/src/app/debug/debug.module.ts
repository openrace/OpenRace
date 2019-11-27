import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MqttComponent } from './mqtt/mqtt.component';

@NgModule({
  declarations: [MqttComponent],
  imports: [
    CommonModule
  ]
})
export class DebugModule { }
