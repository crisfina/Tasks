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
import { forkJoin } from 'rxjs';

import { CategoryService } from '../../../core/categories/category';
import { Category } from '../../../core/categories/category.models';
import { RoomService } from '../../../core/rooms/room';
import { Room } from '../../../core/rooms/room.models';
import {
  Difficulty,
  Priority,
  RepeatType,
  Urgency,
} from '../../../core/tasks/task.models';
import { TaskService } from '../../../core/tasks/task.service';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-task-create',
  styleUrl: './task-create.scss',
  templateUrl: './task-create.html',
})
export class TaskCreate implements OnInit {
  private readonly categoryService = inject(CategoryService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly roomService = inject(RoomService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly categories = signal<Category[]>([]);
  readonly areas = signal<Room[]>([]);
  readonly householdId = signal<number | null>(null);
  readonly returnUrl = signal('/home');

  readonly taskForm = this.formBuilder.nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    category_id: [0],
    room_id: [0],
    estimated_minutes: [null as number | null, [Validators.min(1)]],
    due_date: [this.getTodayForInput(), [Validators.required]],
    difficulty: ['medium' as Difficulty],
    priority: ['medium' as Priority],
    urgency: ['medium' as Urgency],
    repeat_type: ['' as RepeatType | ''],
    repeat_interval: [1, [Validators.min(1)]],
  });

  ngOnInit(): void {
    const householdId = Number(
      this.route.snapshot.queryParamMap.get('householdId'),
    );

    if (Number.isInteger(householdId) && householdId > 0) {
      this.householdId.set(householdId);
      this.returnUrl.set(`/hogares/${householdId}`);
      this.loadHouseholdOptions(householdId);
      return;
    }

    this.loadPersonalCategories();
  }

  submit(): void {
    if (this.taskForm.invalid) {
      this.taskForm.markAllAsTouched();
      return;
    }

    const formValue = this.taskForm.getRawValue();
    const repeatType = formValue.repeat_type || null;
    const householdId = this.householdId();

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.taskService
      .createTask({
        title: formValue.title,
        description: formValue.description || null,
        category_id: formValue.category_id || null,
        room_id:
          householdId === null
            ? null
            : formValue.room_id || null,
        estimated_minutes: formValue.estimated_minutes,
        difficulty: formValue.difficulty,
        priority: formValue.priority,
        urgency: formValue.urgency,
        visibility: householdId === null ? 'private' : 'shared',
        household_id: householdId,
        assignment_mode: 'none',
        days_until_due: this.getDaysUntilDue(formValue.due_date),
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
            'No se ha podido crear la tarea. Inténtalo de nuevo.',
          );
        },
      });
  }

  cancel(): void {
    this.router.navigateByUrl(this.returnUrl());
  }

  private loadPersonalCategories(): void {
    this.categoryService.getPersonalCategories().subscribe({
      next: (categories) =>
        this.categories.set(this.getActiveCategories(categories)),
      error: () => this.categories.set([]),
    });
  }

  private loadHouseholdOptions(householdId: number): void {
    forkJoin({
      areas: this.roomService.getHouseholdRooms(householdId),
      categories: this.categoryService.getHouseholdCategories(householdId),
    }).subscribe({
      next: ({ areas, categories }) => {
        this.areas.set(this.getActiveAreas(areas));
        this.categories.set(this.getActiveCategories(categories));
      },
      error: () => {
        this.areas.set([]);
        this.categories.set([]);
      },
    });
  }

  private getActiveCategories(
    categories: Category[],
  ): Category[] {
    return categories
      .filter((category) => category.is_active)
      .sort(
        (first, second) =>
          (first.display_order ?? 0) -
          (second.display_order ?? 0),
      );
  }

  private getActiveAreas(areas: Room[]): Room[] {
    return areas
      .filter((area) => area.is_active)
      .sort(
        (first, second) =>
          (first.display_order ?? 0) -
          (second.display_order ?? 0),
      );
  }

  private getTodayForInput(): string {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  private getDaysUntilDue(dueDate: string): number {
    const [year, month, day] = dueDate.split('-').map(Number);
    const selectedDate = new Date(year, month - 1, day);

    selectedDate.setHours(0, 0, 0, 0);

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const millisecondsPerDay = 24 * 60 * 60 * 1000;

    return Math.max(
      0,
      Math.round(
        (selectedDate.getTime() - today.getTime()) /
          millisecondsPerDay,
      ),
    );
  }
}