import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';

@Injectable({
  providedIn: 'root'
})
export class RaceService {

  constructor(private messageQueueClientService: MessageQueueClientService) {
  }

  startRace() {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/events/request_start', '1');
  }

  stopRace() {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/events/request_stop', '1');
  }

  setMinLapTime(minLapTimeInSeconds: number) {
    this.messageQueueClientService
      .publishToTopicUnretained('/OpenRace/race/settings/min_lap_time_in_seconds', minLapTimeInSeconds.toString());
  }

  setStartDelay(startDelayInSeconds: number) {
    this.messageQueueClientService
      .publishToTopicUnretained('/OpenRace/race/settings/start_delay_in_seconds', startDelayInSeconds.toString());
  }

  setAmountOfLaps(amountOfLaps: number) {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/race/settings/amount_laps', amountOfLaps.toString());
  }

  setRaceMw(raceMw: number) {
    this.messageQueueClientService.publishToTopicUnretained('/OpenRace/race/settings/race_mw', raceMw.toString());
  }
}
