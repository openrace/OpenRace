import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RaceControlComponent } from './race-control/race-control.component';
import { MaterialModule } from '../material/material.module';
import { FormsModule } from '@angular/forms';
import { FreeflightControlComponent } from './freeflight-control/freeflight-control.component';

@NgModule({
  declarations: [RaceControlComponent, FreeflightControlComponent],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule
  ],
  exports: [
    RaceControlComponent,
    FreeflightControlComponent
  ]
})
export class OpenRaceRaceModule { }
