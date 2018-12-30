import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LedStripsListComponent } from './led-strips-list/led-strips-list.component';
import { MaterialModule } from '../material/material.module';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [LedStripsListComponent],
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
