import {
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import { TaskService } from '../../../core/tasks/task.service';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-task-occurrence-edit',
  styleUrl: './task-occurrence-edit.scss',
  templateUrl: './task-occurrence-edit.html',
})
export class TaskOccurrenceEdit implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly isLoading = signal(true);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly occurrenceId = signal<number | null>(null);
  readonly returnUrl = signal('/home');

  readonly occurrenceForm = this.formBuilder.nonNullable.group({
    available_from: ['', [Validators.required]],
    due_date: ['', [Validators.required]],
    notes: [''],
  });

  ngOnInit(): void {
    const occurrenceId = Number(
      this.route.snapshot.paramMap.get('occurrenceId'),
    );

    if (!Number.isInteger(occurrenceId) || occurrenceId <= 0) {
      this.router.navigateByUrl('/home');
      return;
    }

    this.occurrenceId.set(occurrenceId);
    this.setReturnUrl();
    this.loadOccurrence(occurrenceId);
  }

  submit(): void {
    const occurrenceId = this.occurrenceId();

    if (
      occurrenceId === null ||
      this.occurrenceForm.invalid
    ) {
      this.occurrenceForm.markAllAsTouched();
      return;
    }

    const formValue = this.occurrenceForm.getRawValue();
    const availableFrom = this.getStartOfDay(
      formValue.available_from,
    );
    const dueDate = this.getEndOfDay(formValue.due_date);

    if (dueDate < availableFrom) {
      this.errorMessage.set(
        'La fecha límite no puede ser anterior a la fecha de disponibilidad.',
      );
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.taskService
      .updateOccurrence(occurrenceId, {
        available_from: availableFrom.toISOString(),
        due_date: dueDate.toISOString(),
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
            'No se ha podido guardar la ocurrencia. Inténtalo de nuevo.',
          );
        },
      });
  }

  cancel(): void {
    this.router.navigateByUrl(this.returnUrl());
  }

  private setReturnUrl(): void {
    const returnTo =
      this.route.snapshot.queryParamMap.get('returnTo');
    const householdId = Number(
      this.route.snapshot.queryParamMap.get('householdId'),
    );

    if (
      returnTo === 'grupo' &&
      Number.isInteger(householdId) &&
      householdId > 0
    ) {
      this.returnUrl.set(`/hogares/${householdId}`);
      return;
    }

    if (returnTo === 'personales') {
      this.returnUrl.set('/personales');
    }
  }

  private loadOccurrence(occurrenceId: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.taskService.getOccurrence(occurrenceId).subscribe({
      next: (occurrence) => {
        this.occurrenceForm.setValue({
          available_from: this.getDateForInput(
            occurrence.available_from,
          ),
          due_date: this.getDateForInput(
            occurrence.due_date,
          ),
          notes: occurrence.notes ?? '',
        });
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set(
          'No se ha podido cargar la ocurrencia.',
        );
        this.isLoading.set(false);
      },
    });
  }

  private getDateForInput(value: string): string {
    const date = new Date(value);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  private getStartOfDay(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);

    return new Date(year, month - 1, day, 0, 0, 0, 0);
  }

  private getEndOfDay(value: string): Date {
    const [year, month, day] = value.split('-').map(Number);

    return new Date(year, month - 1, day, 23, 59, 59, 999);
  }
}