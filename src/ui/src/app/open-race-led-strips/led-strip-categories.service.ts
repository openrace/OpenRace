import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { QueueMessage } from '../open-race-common/queue-message';

@Injectable({
  providedIn: 'root'
})
export class LedStripCategoriesService {

  constructor(private messageQueueClientService: MessageQueueClientService) {
    this._ledStripCategories = new BehaviorSubject<string[]>([]);
    this.ledStripCategories = this._ledStripCategories.asObservable();
    this.listenToLedStripCategoriesUpdates();
  }

  ledStripCategories: Observable<string[]>;
  private _ledStripCategories: BehaviorSubject<string[]>;

  private listenToLedStripCategoriesUpdates() {
    this.messageQueueClientService.subscribeToTopic('/OpenRace/provide/led_strip_categories')
      .subscribe(message => this.processLedStripCategoriesMessage(message));
  }

  private processLedStripCategoriesMessage(message: QueueMessage) {
    console.log(`Received message ${message.message} Topic ${message.topic}`);

    const categories: string[] = message.message.split(',');
    this._ledStripCategories.next(categories);
  }
}
