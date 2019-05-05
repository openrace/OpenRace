import { Component, OnInit } from '@angular/core';
import { LedStrip } from '../led-strip';
import { LedStripsService } from '../led-strips.service';
import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';


@Component({
  selector: 'app-led-strips-list',
  templateUrl: './led-strips-list.component.html',
  styleUrls: ['./led-strips-list.component.css']
})
export class LedStripsListComponent implements OnInit {
  ledStrips: LedStrip[] = [];

  constructor(private ledStripService: LedStripsService) {
    this.ledStripService.ledStrips.subscribe(newLedStrips => this.ledStrips = newLedStrips);
  }

  ngOnInit() {
  }

  drop(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.ledStrips, event.previousIndex, event.currentIndex);
    for (let i = 0; i < this.ledStrips.length; i++) {
      this.ledStrips[i].order = i.toString();
      this.ledStripService.updateLedStripOrder(this.ledStrips[i]);
    }
  }

  testFlashLedStrip(event, ledStripId) {
    this.ledStripService.testFlashLedStrip(ledStripId);
    // needed to not expand panel while testing led
    event.stopPropagation();
  }
}
