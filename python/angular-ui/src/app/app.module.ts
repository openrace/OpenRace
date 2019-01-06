import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { FlexLayoutModule } from '@angular/flex-layout';
import { OpenRacePilotsModule } from './open-race-pilots/open-race-pilots.module';
import { MaterialModule } from './material/material.module';
import { OpenRaceLedStripsModule } from './open-race-led-strips/open-race-led-strips.module';
import { OpenRaceRaceModule } from './open-race-race/open-race-race.module';


@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    FlexLayoutModule,
    MaterialModule,
    OpenRacePilotsModule,
    OpenRaceLedStripsModule,
    OpenRaceRaceModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
