export class Pilot {
  constructor(public id: string) {
    this.name = `Pilot ${id}`;
  }

  name: string;
  enabled: boolean;
  band: string;
  channel: number;
  frequency: string;
  gain: number;
}
