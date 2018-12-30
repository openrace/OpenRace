import { Component, OnInit } from '@angular/core';
import { LedStrip } from '../led-strip';
import { LedStripsService } from '../led-strips.service';

@Component({
  selector: 'app-led-strips-list',
  templateUrl: './led-strips-list.component.html',
  styleUrls: ['./led-strips-list.component.css']
})
export class LedStripsListComponent implements OnInit {
  ledStrips: LedStrip[] = [];

  constructor(private ledStripsService: LedStripsService) {
    this.ledStripsService.ledStrips.subscribe(newLedStrips => this.ledStrips = newLedStrips);
  }

  ngOnInit() {
  }

}
