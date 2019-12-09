import { MessageQueueClientService } from 'src/app/open-race-common/message-queue-client.service';
import { QueueMessage } from 'src/app/open-race-common/queue-message';

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-message-history',
  templateUrl: './message-history.component.html',
  styleUrls: ['./message-history.component.scss']
})
export class MessageHistoryComponent implements OnInit {
  public messages = new Array<[Date, QueueMessage]>();

  constructor(private readonly messageQueueClientService: MessageQueueClientService) { }

  ngOnInit() {
    this.messageQueueClientService.subscribeToTopic('/#').subscribe(message => {
       this.messages = [[new Date(), message], ...this.messages];
    });
  }

  clear() {
    this.messages = new Array<[Date, QueueMessage]>();
  }
}
