import { MessageQueueClientService } from 'src/app/open-race-common/message-queue-client.service';

import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-publish-message',
  templateUrl: './publish-message.component.html',
  styleUrls: ['./publish-message.component.scss']
})
export class PublishMessageComponent implements OnInit {
  public topic: string;

  public message: string;

  constructor(private readonly messageQueueClientService: MessageQueueClientService) { }

  ngOnInit() {
  }

  public publish() {
    this.messageQueueClientService.publishToTopic(this.topic, this.message);
  }
}
