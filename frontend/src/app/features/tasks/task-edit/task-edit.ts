import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { CategoryService } from '../../../core/categories/category';
import { Category } from '../../../core/categories/category.models';
import { TaskService } from '../../../core/tasks/task.service';
import {
  Difficulty,
  Priority,
  RepeatType,
  Urgency,
} from '../../../core/tasks/task.models';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-task-edit',
  styleUrl: './task-edit.scss',
  templateUrl: './task-edit.html',
})
export class TaskEdit implements OnInit {
  private readonly categoryService = inject(CategoryService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly isLoading = signal(true);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly taskId = signal<number | null>(null);
  readonly categories = signal<Category[]>([]);
  readonly returnUrl = signal('/personales');

  readonly taskForm = this.formBuilder.nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    category_id: [0],
    estimated_minutes: [null as number | null, [Validators.min(1)]],
    difficulty: ['medium' as Difficulty],
    priority: ['medium' as Priority],
    urgency: ['medium' as Urgency],
    repeat_type: ['' as RepeatType | ''],
    repeat_interval: [1, [Validators.min(1)]],
  });

  ngOnInit(): void {
    const returnTo = this.route.snapshot.queryParamMap.get('returnTo');

    if (returnTo === 'home') {
      this.returnUrl.set('/home');
    }

    const taskId = Number(this.route.snapshot.paramMap.get('taskId'));

    if (!Number.isInteger(taskId) || taskId <= 0) {
      this.router.navigateByUrl(this.returnUrl());
      return;
    }

    this.taskId.set(taskId);
    this.loadCategories();

    this.taskService.getTask(taskId).subscribe({
      next: (task) => {
        this.taskForm.setValue({
          title: task.title,
          description: task.description ?? '',
          category_id: task.category_id ?? 0,
          estimated_minutes: task.estimated_minutes,
          difficulty: task.difficulty,
          priority: task.priority,
          urgency: task.urgency,
          repeat_type: task.repeat_type ?? '',
          repeat_interval: task.repeat_interval ?? 1,
        });

        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se ha podido cargar la tarea.');
        this.isLoading.set(false);
      },
    });
  }

  submit(): void {
    const taskId = this.taskId();

    if (taskId === null || this.taskForm.invalid) {
      this.taskForm.markAllAsTouched();
      return;
    }

    const formValue = this.taskForm.getRawValue();
    const repeatType = formValue.repeat_type || null;

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.taskService
      .updateTask(taskId, {
        title: formValue.title,
        description: formValue.description || null,
        category_id: formValue.category_id || null,
        estimated_minutes: formValue.estimated_minutes,
        difficulty: formValue.difficulty,
        priority: formValue.priority,
        urgency: formValue.urgency,
        repeat_type: repeatType,
        repeat_interval: repeatType ? formValue.repeat_interval : null,
      })
      .subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.router.navigateByUrl(this.returnUrl());
        },
        error: () => {
          this.isSubmitting.set(false);
          this.errorMessage.set(
            'No se ha podido guardar la tarea. Inténtalo de nuevo.',
          );
        },
      });
  }

  cancel(): void {
    this.router.navigateByUrl(this.returnUrl());
  }

  private loadCategories(): void {
    this.categoryService.getPersonalCategories().subscribe({
      next: (categories) =>
        this.categories.set(
          categories
            .filter((category) => category.is_active)
            .sort(
              (first, second) =>
                (first.display_order ?? 0) - (second.display_order ?? 0),
            ),
        ),
      error: () => this.categories.set([]),
    });
  }
}