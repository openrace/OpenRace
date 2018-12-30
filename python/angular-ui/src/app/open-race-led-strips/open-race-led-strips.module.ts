import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LedStripsListComponent } from './led-strips-list/led-strips-list.component';
import { MaterialModule } from '../material/material.module';
import { FormsModule } from '@angular/forms';
import { EditLedStripComponent } from './edit-led-strip/edit-led-strip.component';

@NgModule({
  declarations: [LedStripsListComponent, EditLedStripComponent],
  imports: [
    CommonModule,
    MaterialModule,
    FormsModule
  ],
  exports: [
    LedStripsListComponent
  ]
})
export class OpenRaceLedStripsModule { }
