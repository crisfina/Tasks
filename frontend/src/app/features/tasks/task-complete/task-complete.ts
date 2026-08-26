import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { TaskService } from '../../../core/tasks/task.service';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-task-complete',
  styleUrl: './task-complete.scss',
  templateUrl: './task-complete.html',
})
export class TaskComplete implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly occurrenceId = signal<number | null>(null);

  readonly completionForm = this.formBuilder.nonNullable.group({
    realized_minutes: [1, [Validators.required, Validators.min(1)]],
    notes: [''],
  });

  ngOnInit(): void {
    const occurrenceId = Number(this.route.snapshot.paramMap.get('occurrenceId'));

    if (!Number.isInteger(occurrenceId) || occurrenceId <= 0) {
      this.router.navigateByUrl('/home');
      return;
    }

    this.occurrenceId.set(occurrenceId);
  }

  submit(): void {
    const occurrenceId = this.occurrenceId();

    if (occurrenceId === null || this.completionForm.invalid) {
      this.completionForm.markAllAsTouched();
      return;
    }

    const formValue = this.completionForm.getRawValue();

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.taskService
      .completeOccurrence(occurrenceId, {
        realized_minutes: formValue.realized_minutes,
        notes: formValue.notes || null,
      })
      .subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.router.navigateByUrl('/home');
        },
        error: () => {
          this.isSubmitting.set(false);
          this.errorMessage.set(
            'No se ha podido completar la tarea. Inténtalo de nuevo.',
          );
        },
      });
  }

  cancel(): void {
    this.router.navigateByUrl('/home');
  }
}