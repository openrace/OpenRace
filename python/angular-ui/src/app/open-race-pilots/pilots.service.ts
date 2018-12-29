import { Injectable } from '@angular/core';
import { MessageQueueClientService } from '../open-race-common/message-queue-client.service';
import { Pilot } from './pilots-list/pilots-list.component';

@Injectable({
  providedIn: 'root'
})
export class PilotsService {
  constructor(private messageQueueClientService: MessageQueueClientService) {
  }

  activatePilot(pilotId: string) {
    console.log('Activated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, 'enabled', true);
  }

  deactivatePilot(pilotId: string) {
    console.log('Deactivated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, 'enabled', false);
  }

  updatePilot(pilot: Pilot) {
    // frequency, band, channel, name
    const pilotId = pilot.id;

    this.publishPilotMessage(pilotId, 'name', pilot.name);
    this.publishPilotMessage(pilotId, 'band', pilot.band);
    this.publishPilotMessage(pilotId, 'channel', pilot.channel);
    this.publishPilotMessage(pilotId, 'frequency', pilot.frequency);
    this.publishPilotMessage(pilotId, 'gain', pilot.gain);

  }

  private publishPilotMessage(pilotId: string, pilotSubTopic: string, value: any) {
    this.messageQueueClientService.publishToTopic(`${'/OpenRace/pilots/' + pilotId}/${pilotSubTopic}`, value.toString());
  }
}
