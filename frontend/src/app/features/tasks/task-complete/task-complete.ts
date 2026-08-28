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
  readonly returnUrl = signal('/home');

  readonly completionForm = this.formBuilder.nonNullable.group({
    realized_minutes: [1, [Validators.required, Validators.min(1)]],
    notes: [''],
  });

  ngOnInit(): void {
    this.configureReturnUrl();

    const occurrenceId = Number(this.route.snapshot.paramMap.get('occurrenceId'));

    if (!Number.isInteger(occurrenceId) || occurrenceId <= 0) {
      this.router.navigateByUrl(this.returnUrl());
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
          this.router.navigateByUrl(this.returnUrl());
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
    this.router.navigateByUrl(this.returnUrl());
  }

  private configureReturnUrl(): void {
    const returnTo = this.route.snapshot.queryParamMap.get('returnTo');

  if (returnTo === 'personales') {
    this.returnUrl.set('/personales');
  } else if (returnTo === 'hogares') {
    this.returnUrl.set('/hogares');
  } else if (returnTo === 'grupo') {
    const householdId = Number(
      this.route.snapshot.queryParamMap.get('householdId'),
    );

    if (Number.isInteger(householdId) && householdId > 0) {
      this.returnUrl.set(`/hogares/${householdId}`);
    }
  }

    if (returnTo !== 'grupo') {
      return;
    }

    const householdId = Number(
      this.route.snapshot.queryParamMap.get('householdId'),
    );

    if (Number.isInteger(householdId) && householdId > 0) {
      this.returnUrl.set(`/hogares/${householdId}`);
    }
  }
}