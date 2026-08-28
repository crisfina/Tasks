import { Component, EventEmitter, Input, Output } from '@angular/core';

import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';
import { TaskCard } from '../task-card/task-card';

export interface TaskListItem {
  task: Task;
  occurrence: TaskOccurrence | null;
  statusLabel?: string;
}

@Component({
  imports: [TaskCard],
  selector: 'app-task-list',
  styleUrl: './task-list.scss',
  templateUrl: './task-list.html',
})
export class TaskList {
  @Input({ required: true }) items: TaskListItem[] = [];

  @Output() edit = new EventEmitter<number>();
  @Output() complete = new EventEmitter<number>();
  @Output() delete = new EventEmitter<Task>();
  @Input() isEditable = true;
  @Input() showComplete = true;
  @Input() showDelete = true;
}