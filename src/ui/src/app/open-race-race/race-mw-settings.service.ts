import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { QueueMessage } from '../open-race-common/queue-message';

@Injectable({
  providedIn: 'root'
})
export class RaceMwSettingsService {

  constructor(private messageQueueClientService: MessageQueueClientService) {
    this._raceMwSettings = new BehaviorSubject<number[]>([]);
    this.raceMwSettings = this._raceMwSettings.asObservable();
    this.listenToRaceMwSettingsUpdates();
  }

  raceMwSettings: Observable<number[]>;
  private _raceMwSettings: BehaviorSubject<number[]>;

  private listenToRaceMwSettingsUpdates() {
    this.messageQueueClientService.subscribeToTopic('/OpenRace/provide/race_mw')
      .subscribe(message => this.processRaceMwSettingsMessage(message));
  }

  private processRaceMwSettingsMessage(message: QueueMessage) {
    console.log(`Received message ${message.message} Topic ${message.topic}`);

    const categories: number[] = message.message.split(',').map(item => parseInt(item, 10));
    this._raceMwSettings.next(categories);
  }
}
