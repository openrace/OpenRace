import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FrequencyChooserComponent} from './frequency-chooser/frequency-chooser.component';
import {MaterialModule} from "../material/material.module";

@NgModule({
  declarations: [FrequencyChooserComponent],
  imports: [
    CommonModule,
    MaterialModule
  ],
  exports: [
    FrequencyChooserComponent
  ]
})
export class OpenRacePilotsModule {
}
