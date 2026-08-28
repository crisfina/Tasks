import { Component, EventEmitter, Input, Output } from '@angular/core';

import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';

@Component({
  imports: [],
  selector: 'app-task-card',
  styleUrl: './task-card.scss',
  templateUrl: './task-card.html',
})
export class TaskCard {
  @Input({ required: true }) task!: Task;
  @Input() occurrence: TaskOccurrence | null = null;
  @Input() statusLabel = 'Pendiente';
  @Input() isEditable = true;
  @Input() showComplete = true;
  @Input() showDelete = true;

  @Output() edit = new EventEmitter<number>();
  @Output() complete = new EventEmitter<number>();
  @Output() delete = new EventEmitter<Task>();

  editTask(): void {
    if (this.isEditable) {
      this.edit.emit(this.task.id);
    }
  }

  completeTask(event: MouseEvent): void {
    event.stopPropagation();

    if (this.occurrence !== null) {
      this.complete.emit(this.occurrence.id);
    }
  }

  deleteTask(event: MouseEvent): void {
    event.stopPropagation();
    this.delete.emit(this.task);
  }
}