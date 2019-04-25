import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BrowserModule } from '@angular/platform-browser';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {
  MatButtonModule,
  MatCardModule, MatDividerModule, MatExpansionModule,
  MatFormFieldModule,
  MatInputModule,
  MatSelectModule, MatSliderModule, MatSlideToggleModule,
  MatTabsModule,
  MatToolbarModule
} from '@angular/material';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { FlexLayoutModule } from '@angular/flex-layout';

@NgModule({
  declarations: [],
  imports: [],
  exports: [
    CommonModule,
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
    DragDropModule,
    MatSlideToggleModule,
    MatSliderModule,
    FlexLayoutModule,
  ]
})
export class MaterialModule {
}