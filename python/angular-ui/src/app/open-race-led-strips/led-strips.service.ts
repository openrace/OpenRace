import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { BehaviorSubject, Observable } from 'rxjs';
import { QueueMessage } from '../open-race-common/queue-message';
import { LedStrip } from './led-strip';

@Injectable({
  providedIn: 'root'
})
export class LedStripsService {

  constructor(private messageQueueClientService: MessageQueueClientService) {
    this._ledStrips = new BehaviorSubject<LedStrip[]>([]);
    this.ledStrips = this._ledStrips.asObservable();
    this.listenToLedStripUpdates();
  }

  ledStrips: Observable<LedStrip[]>;
  private _ledStrips: BehaviorSubject<LedStrip[]>;
  private ledStripsStore: Map<string, LedStrip> = new Map<string, LedStrip>();

  private static applyLedStripUpdate(property: string, ledStrip: LedStrip, value: string) {
    switch (property) {
      case 'category':
        ledStrip.category = value;
        break;
      case 'order':
        ledStrip.order = value;
        break;
    }
  }

  updateLedStrips(ledStrip: LedStrip) {
    const ledStripId = ledStrip.id;

    this.publishLedStripMessage(ledStripId, 'category', ledStrip.category);
    this.publishLedStripMessage(ledStripId, 'order', ledStrip.order);
  }

  private publishLedStripMessage(letStripId: string, ledStripSubTopic: string, value: any) {
    this.messageQueueClientService.publishToTopic(`${'/OpenRace/led/' + letStripId}/${ledStripSubTopic}`, value.toString());
  }

  private listenToLedStripUpdates() {
    this.messageQueueClientService.subscribeToTopic('/OpenRace/led/#').subscribe(message => this.processLedStripMessage(message));
  }

  private processLedStripMessage(message: QueueMessage) {
    console.log(`Received message ${message.message} Topic ${message.topic}`);

    const topicParts = /\/OpenRace\/led\/([a-fA-F0-9:]*)\/([a-zA-Z0-9]*)/.exec(message.topic);
    if (topicParts != null) {
      this.updateLedStripFromMessage(topicParts[1].toString(), topicParts[2].toString(), message.message);
    }
  }

  testFlashLedStrip(letStripId: string) {
    this.messageQueueClientService.publishToTopicUnretained(`${'/d1ws2812/' + letStripId}`, '6;0;0;255');
  }

  private updateLedStripFromMessage(ledStripId: string, property: string, value: string) {
    console.log(`Updating property ${property} of LedStrip with ledStripId ${ledStripId}`);

    LedStripsService.applyLedStripUpdate(property, this.safeGetLedStrip(ledStripId), value);

    console.log(Array.from(this.ledStripsStore.values()));
    this._ledStrips.next(Array.from(this.ledStripsStore.values()).sort((a: LedStrip, b: LedStrip) => a.id >= b.id ? 1 : -1));
  }

  private safeGetLedStrip(ledStripId: string) {
    if (!this.ledStripsStore.has(ledStripId)) {
      this.ledStripsStore.set(ledStripId, new LedStrip(ledStripId));
    }
    return this.ledStripsStore.get(ledStripId);
  }
}
