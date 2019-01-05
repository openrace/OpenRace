import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { QueueMessage } from '../open-race-common/queue-message';
import { Pilot } from './pilot';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PilotsService {

  constructor(private messageQueueClientService: MessageQueueClientService) {
    this._pilots = new BehaviorSubject<Pilot[]>([]);
    this.pilots = this._pilots.asObservable();
    this.listenToPilotUpdates();
  }

  pilots: Observable<Pilot[]>;
  private _pilots: BehaviorSubject<Pilot[]>;
  private pilotsStore: Map<string, Pilot> = new Map<string, Pilot>();

  private static applyPilotUpdate(property: string, pilot, value: string) {
    switch (property) {
      case 'name':
        pilot.name = value;
        break;
      case 'band':
        pilot.band = value;
        break;
      case 'channel':
        pilot.channel = value;
        break;
      case 'frequency':
        pilot.frequency = value;
        break;
      case 'gain':
        pilot.gain = Number(value);
        break;
      case 'enabled':
        pilot.enabled = value === '0' ? false : true;
        break;
    }
  }

  activatePilot(pilotId: string) {
    console.log('Activated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, 'enabled', '1');
  }

  deactivatePilot(pilotId: string) {
    console.log('Deactivated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, 'enabled', '0');
  }

  updatePilot(pilot: Pilot) {
    const pilotId = pilot.id;

    this.publishPilotMessage(pilotId, 'name', pilot.name);
    this.publishPilotMessage(pilotId, 'band', pilot.band);
    this.publishPilotMessage(pilotId, 'channel', pilot.channel);
    this.publishPilotMessage(pilotId, 'frequency', pilot.frequency)
  }

  private publishPilotMessage(pilotId: string, pilotSubTopic: string, value: any) {
    this.messageQueueClientService.publishToTopic(`${'/OpenRace/pilots/' + pilotId}/${pilotSubTopic}`, value.toString());
  }

  private listenToPilotUpdates() {
    this.messageQueueClientService.subscribeToTopic('/OpenRace/pilots/#').subscribe(message => this.processPilotMessage(message));
  }

  private processPilotMessage(message: QueueMessage) {
    console.log(`Received message ${message.message} Topic ${message.topic}`);

    const topicParts = /\/OpenRace\/pilots\/([0-9])\/([a-zA-Z0-9]*)/.exec(message.topic);
    if (topicParts != null) {
      this.updatePilotFromMessage(topicParts[1].toString(), topicParts[2].toString(), message.message);
    }
  }

  private updatePilotFromMessage(pilotId: string, property: string, value: string) {
    console.log(`Updating property ${property} of Pilot with pilotId ${pilotId}`);

    PilotsService.applyPilotUpdate(property, this.safeGetPilot(pilotId), value);

    console.log(Array.from(this.pilotsStore.values()));
    this._pilots.next(Array.from(this.pilotsStore.values()).sort((a: Pilot, b: Pilot) => a.id >= b.id ? 1 : -1));
  }

  private safeGetPilot(pilotId: string) {
    if (!this.pilotsStore.has(pilotId)) {
      this.pilotsStore.set(pilotId, new Pilot(pilotId));
    }
    return this.pilotsStore.get(pilotId);
  }
}
