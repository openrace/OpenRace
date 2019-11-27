import { NgModule } from '@angular/core';
import { FlexLayoutModule } from '@angular/flex-layout';
import { RouterModule } from '@angular/router';

import { AppComponent } from './app.component';
import { DebugMessageQueueComponent } from './debug/debug-message-queue/debug-message-queue.component';
import { DebugModule } from './debug/debug.module';
import { MaterialModule } from './material/material.module';
import { LedStripsListComponent } from './open-race-led-strips/led-strips-list/led-strips-list.component';
import { OpenRaceLedStripsModule } from './open-race-led-strips/open-race-led-strips.module';
import { OpenRacePilotsModule } from './open-race-pilots/open-race-pilots.module';
import { PilotsListComponent } from './open-race-pilots/pilots-list/pilots-list.component';
import { OpenRaceRaceModule } from './open-race-race/open-race-race.module';
import { RaceControlComponent } from './open-race-race/race-control/race-control.component';

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
    DebugModule,
    RouterModule.forRoot([
      {path: 'fly', component: RaceControlComponent},
      {path: 'pilots', component: PilotsListComponent},
      {path: 'ledstrips', component: LedStripsListComponent},
      {path: 'debug', component: DebugMessageQueueComponent},
      {path: '', redirectTo: '/fly', pathMatch: 'full'}
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule {
}
