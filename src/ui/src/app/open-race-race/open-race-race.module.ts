import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RaceControlComponent } from './race-control/race-control.component';
import { MaterialModule } from '../material/material.module';
import { FormsModule } from '@angular/forms';
import { RaceSettingsComponent } from './race-settings/race-settings.component';

@NgModule({
  declarations: [RaceControlComponent, RaceSettingsComponent],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule
  ],
  exports: [
    RaceControlComponent
  ],
  entryComponents: [
    RaceSettingsComponent
  ]
})
export class OpenRaceRaceModule { }
