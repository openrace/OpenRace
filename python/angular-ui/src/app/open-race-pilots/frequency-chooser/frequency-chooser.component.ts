import {Component, Input, OnInit} from '@angular/core';
import {Pilot} from "../pilots-list/pilots-list.component";

@Component({
  selector: 'app-frequency-chooser',
  templateUrl: './frequency-chooser.component.html',
  styleUrls: ['./frequency-chooser.component.css']
})
export class FrequencyChooserComponent implements OnInit {

  bands: string[] = ['A', 'B', 'E', 'Fatshark', 'Raceband'];
  channels: string[] = ['1', '2', '3', '4', '5', '6', '7', '8'];
  frequencies: { [id: string]: string } = {
    'A1': '5865',
    'A2': '5845',
    'A3': '5825',
    'A4': '5805',
    'A5': '5785',
    'A6': '5765',
    'A7': '5745',
    'A8': '5725',
    'B1': '5733',
    'B2': '5752',
    'B3': '5771',
    'B4': '5790',
    'B5': '5809',
    'B6': '5828',
    'B7': '5847',
    'B8': '5866',
    'E1': '5705',
    'E2': '5685',
    'E3': '5665',
    'E4': '5645',
    'E5': '5885',
    'E6': '5905',
    'E7': '5925',
    'E8': '5945',
    'Fatshark1': '5740',
    'Fatshark2': '5760',
    'Fatshark3': '5780',
    'Fatshark4': '5800',
    'Fatshark5': '5820',
    'Fatshark6': '5840',
    'Fatshark7': '5860',
    'Fatshark8': '5880',
    'Raceband1': '5658',
    'Raceband2': '5695',
    'Raceband3': '5732',
    'Raceband4': '5769',
    'Raceband5': '5806',
    'Raceband6': '5843',
    'Raceband7': '5880',
    'Raceband8': '5917',
  };

  @Input() private pilot: Pilot;

  ngOnInit() {
  }

  updateFrequency() {
    console.log(`Updating frequency with band ${this.pilot.band} and channel ${this.pilot.channel}`);
    this.pilot.frequency = this.frequencies[this.pilot.band + this.pilot.channel];
  }
}
