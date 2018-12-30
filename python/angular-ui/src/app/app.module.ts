import {NgModule} from '@angular/core';

import {AppComponent} from './app.component';
import {FlexLayoutModule} from '@angular/flex-layout';
import {OpenRacePilotsModule} from './open-race-pilots/open-race-pilots.module';
import {MaterialModule} from './material/material.module';


@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    FlexLayoutModule,
    MaterialModule,
    OpenRacePilotsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
