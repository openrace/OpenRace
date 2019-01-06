import { Component, Input, OnInit } from '@angular/core';
import { Pilot } from '../pilot';
import { Band } from './band';

@Component({
  selector: 'app-frequency-chooser',
  templateUrl: './frequency-chooser.component.html',
  styleUrls: ['./frequency-chooser.component.css']
})
export class FrequencyChooserComponent implements OnInit {

  bands: Band[] = [
    new Band('1', 'Low Race / Diatone'),
    new Band('2', 'IRC / Fatshark / Airwave/ F'),
    new Band('3', 'Race Band / r'),
    new Band('4', 'Boscam E Lumenier / DJI / E'),
    new Band('5', 'Boscam B'),
    new Band('6', 'Boscam A / Team Black Sheep / A'),
    new Band('7', 'U'),
    new Band('8', 'O'),
    new Band('9', 'L'),
    new Band('10', 'Raceband V2 / H')];
  channels: number[] = [1, 2, 3, 4, 5, 6, 7, 8];
  frequencies: { [id: string]: number[] } = {
    '1': [5362, 5399, 5436, 5473, 5510, 5547, 5584, 5621],
    '2': [5740, 5760, 5780, 5800, 5820, 5840, 5860, 5880],
    '3': [5658, 5695, 5732, 5769, 5806, 5843, 5880, 5917],
    '4': [5705, 5685, 5665, 5645, 5885, 5905, 5925, 5945],
    '5': [5733, 5752, 5771, 5790, 5809, 5828, 5847, 5866],
    '6': [5865, 5845, 5825, 5805, 5785, 5765, 5745, 5725],
    '7': [5325, 5348, 5366, 5384, 5402, 5420, 5438, 5456],
    '8': [5474, 5492, 5510, 5528, 5546, 5564, 5582, 5600],
    '9': [5333, 5373, 5413, 5453, 5493, 5533, 5573, 5613],
    '10': [5653, 5693, 5733, 5773, 5813, 5853, 5893, 5933],
  };

  @Input() private pilot: Pilot;

  ngOnInit() {
  }

  updateFrequency() {
    console.log(`Updating frequency with band ${this.pilot.band} and channel ${this.pilot.channel}`);
    this.pilot.frequency = this.frequencies[this.pilot.band][this.pilot.channel - 1].toString();
  }
}
