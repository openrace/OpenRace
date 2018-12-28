import {NgModule} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FrequencyChooserComponent} from './frequency-chooser/frequency-chooser.component';
import {MaterialModule} from "../material/material.module";
import {PilotsListComponent} from "./pilots-list/pilots-list.component";
import {FormsModule} from "@angular/forms";
import {PilotsService} from "./pilots.service";
import {OpenRaceCommonModule} from "../open-race-common/open-race-common.module";


@NgModule({
  declarations: [
    FrequencyChooserComponent,
    PilotsListComponent],
  imports: [
    CommonModule,
    FormsModule,
    MaterialModule,
    OpenRaceCommonModule
  ],
  providers: [
    PilotsService
  ],
  exports: [
    PilotsListComponent
  ]
})
export class OpenRacePilotsModule {
}
