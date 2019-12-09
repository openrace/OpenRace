export class QueueMessage {
  constructor(public topic: string, public message: string, public retained: boolean) {
  }
}
