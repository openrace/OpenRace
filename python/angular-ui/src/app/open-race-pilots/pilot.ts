export class Pilot {
  constructor(public id: string) {
  }

  name: string;
  enabled: boolean;
  band: string;
  channel: string;
  frequency: string;
  gain: number;
}
