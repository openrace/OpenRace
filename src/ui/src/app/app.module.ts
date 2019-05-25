import { NgModule } from '@angular/core';

import { AppComponent } from './app.component';
import { FlexLayoutModule } from '@angular/flex-layout';
import { OpenRacePilotsModule } from './open-race-pilots/open-race-pilots.module';
import { MaterialModule } from './material/material.module';
import { OpenRaceLedStripsModule } from './open-race-led-strips/open-race-led-strips.module';
import { OpenRaceRaceModule } from './open-race-race/open-race-race.module';
import { RouterModule, RouterOutlet } from '@angular/router';
import { RaceControlComponent } from './open-race-race/race-control/race-control.component';
import { PilotsListComponent } from './open-race-pilots/pilots-list/pilots-list.component';
import { LedStripsListComponent } from './open-race-led-strips/led-strips-list/led-strips-list.component';


@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    FlexLayoutModule,
    MaterialModule,
    OpenRacePilotsModule,
    OpenRaceLedStripsModule,
    OpenRaceRaceModule,
    RouterModule.forRoot([
      {path: 'fly', component: RaceControlComponent},
      {path: 'pilots', component: PilotsListComponent},
      {path: 'ledstrips', component: LedStripsListComponent},
      {path: '', redirectTo: '/fly', pathMatch: 'full'}
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
