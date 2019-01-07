import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { RaceSettings } from './race-control/race.settings';
import { BehaviorSubject, Observable } from 'rxjs';
import { QueueMessage } from '../open-race-common/queue-message';

@Injectable({
  providedIn: 'root'
})
export class RaceService {

  raceSettings: Observable<RaceSettings>;
  private _raceSettings: BehaviorSubject<RaceSettings> = new BehaviorSubject(new RaceSettings());

  constructor(private messageQueueClientService: MessageQueueClientService) {
    this.raceSettings = this._raceSettings.asObservable();
    this.listenToRaceSettings();
  }

  startRace() {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/race/start', '1');
  }

  stopRace() {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/race/stop', '1');
  }

  setMinLapTime(minLapTimeInSeconds: number) {
    this.messageQueueClientService
      .publishToTopic('/OpenRace/race/settings/min_lap_time_in_seconds', minLapTimeInSeconds.toString());
  }

  setStartDelay(startDelayInSeconds: number) {
    this.messageQueueClientService
      .publishToTopic('/OpenRace/race/settings/start_delay_in_seconds', startDelayInSeconds.toString());
  }

  setAmountOfLaps(amountOfLaps: number) {
    this.messageQueueClientService.publishToTopic('/OpenRace/race/settings/amount_laps', amountOfLaps.toString());
  }

  setRaceMw(raceMw: number) {
    this.messageQueueClientService.publishToTopic('/OpenRace/race/settings/race_mw', raceMw.toString());
  }

  private listenToRaceSettings() {
    this.messageQueueClientService.subscribeToTopic('/OpenRace/race/settings/#')
      .subscribe(message => this.processRaceSettingsMessage(message));
  }

  private processRaceSettingsMessage(message: QueueMessage) {
    console.log(`Received message ${message.message} Topic ${message.topic}`);

    const topicParts = /\/OpenRace\/race\/settings\/([a-zA-Z0-9_]*)/.exec(message.topic);
    if (topicParts != null) {
      this.updateSettingsFromMessage(topicParts[1].toString(), message.message);
    }
  }

  private updateSettingsFromMessage(subTopic: string, message: string) {
    const currentRaceSettings = this._raceSettings.value;
    switch (subTopic) {
      case 'min_lap_time_in_seconds':
        currentRaceSettings.minLapTimeInSeconds = parseInt(message, 10);
        break;
      case 'start_delay_in_seconds':
        currentRaceSettings.startDelayInSeconds = parseInt(message, 10);
        break;
      case 'amount_laps':
        currentRaceSettings.amountOfLaps = parseInt(message, 10);
        break;
      case 'race_mw':
        currentRaceSettings.raceMw = parseInt(message, 10);
        break;
    }

    this._raceSettings.next(currentRaceSettings);
  }
}
