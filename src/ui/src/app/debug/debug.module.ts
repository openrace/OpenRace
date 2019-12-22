import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatCheckbox, MatCheckboxModule } from '@angular/material/checkbox';

import { MaterialModule } from '../material/material.module';
import { DebugMessageQueueComponent } from './debug-message-queue/debug-message-queue.component';
import { MessageHistoryComponent } from './debug-message-queue/message-history/message-history.component';
import { PublishMessageComponent } from './debug-message-queue/publish-message/publish-message.component';

@NgModule({
  declarations: [DebugMessageQueueComponent, PublishMessageComponent, MessageHistoryComponent],
  imports: [
    CommonModule,
    FormsModule,
    MatCheckboxModule,
    MaterialModule
  ]
})
export class DebugModule { }
