import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RaceControlComponent } from './race-control/race-control.component';
import { MaterialModule } from '../material/material.module';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [RaceControlComponent],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule
  ],
  exports: [
    RaceControlComponent
  ]
})
export class OpenRaceRaceModule { }
