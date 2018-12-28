import {Injectable} from '@angular/core';
import {MessageQueueClientService} from "../open-race-common/message-queue-client.service";

@Injectable({
  providedIn: 'root'
})
export class PilotsService {
  private topic: string = '/OpenRace/pilots/';
  private pilotEnabledSubTopic = 'enabled';

  constructor(private messageQueueClientService: MessageQueueClientService) {
  }

  activatePilot(pilotId: string) {
    console.log('Activated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, 'enabled', true);
  }

  deactivatePilot(pilotId: string) {
    console.log('Deactivated pilot ' + pilotId);
    this.publishPilotMessage(pilotId, this.pilotEnabledSubTopic, false);
  }

  private publishPilotMessage(pilotId: string, pilotSubTopic: string, value: any) {
    this.messageQueueClientService.publishToTopic(`${this.topic + pilotId}/${pilotSubTopic}`, value.toString());
  }
}
