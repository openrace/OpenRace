import { Component, Input, OnInit } from '@angular/core';
import { LedStrip } from '../led-strip';
import { LedStripsService } from '../led-strips.service';
import { LedStripCategoriesService } from '../led-strip-categories.service';

@Component({
  selector: 'app-edit-led-strip',
  templateUrl: './edit-led-strip.component.html',
  styleUrls: ['./edit-led-strip.component.css']
})
export class EditLedStripComponent implements OnInit {
  @Input() private ledStrip: LedStrip;

  stripCategories: string[] = ['gate', 'strips_run_forward', 'strips_run_backward', 'start_pod', 'pilot_chip'];

  constructor(private ledStripService: LedStripsService, private ledStripCategoriesService: LedStripCategoriesService) {
    this.ledStripCategoriesService.ledStripCategories.subscribe(next => this.stripCategories = next);
  }

  ngOnInit() {
  }

  updateLedStrip() {
    this.ledStripService.updateLedStrips(this.ledStrip);
  }

  testFlashLedStrip() {
    this.ledStripService.testFlashLedStrip(this.ledStrip.id);
  }
}
