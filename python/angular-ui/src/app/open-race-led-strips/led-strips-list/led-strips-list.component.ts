import { Component, OnInit } from '@angular/core';
import { LedStrip } from '../led-strip';

@Component({
  selector: 'app-led-strips-list',
  templateUrl: './led-strips-list.component.html',
  styleUrls: ['./led-strips-list.component.css']
})
export class LedStripsListComponent implements OnInit {
  ledStrips: LedStrip[] = [new LedStrip('1'), new LedStrip('2')]

  stripCategories: string[] = ['gate', 'run_forward'];

  constructor() {
  }

  ngOnInit() {
  }

}
