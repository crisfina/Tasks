import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';

import { CategoryService } from '../../../core/categories/category';
import { Category } from '../../../core/categories/category.models';
import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';
import { TaskService } from '../../../core/tasks/task.service';
import {
  TaskList,
  TaskListItem,
} from '../../../shared/components/task-list/task-list';

interface PersonalTask {
  task: Task;
  nextOccurrence: TaskOccurrence | null;
}

@Component({
  imports: [TaskList],
  selector: 'app-personal-task-list',
  styleUrl: './personal-task-list.scss',
  templateUrl: './personal-task-list.html',
})
export class PersonalTaskList implements OnInit {
  private readonly categoryService = inject(CategoryService);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);
  readonly personalTasks = signal<PersonalTask[]>([]);
  readonly categories = signal<Category[]>([]);
  readonly selectedCategoryId = signal<number | null>(null);

  readonly filteredPersonalTasks = computed(() => {
    const selectedCategoryId = this.selectedCategoryId();

    if (selectedCategoryId === null) {
      return this.personalTasks();
    }

    return this.personalTasks().filter(
      (personalTask) => personalTask.task.category_id === selectedCategoryId,
    );
  });

  readonly filteredTaskListItems = computed<TaskListItem[]>(() =>
    this.filteredPersonalTasks().map((personalTask) => ({
      task: personalTask.task,
      occurrence: personalTask.nextOccurrence,
    })),
  );

  ngOnInit(): void {
    this.loadTasks();
    this.loadCategories();
  }

  createTask(): void {
    this.router.navigateByUrl('/tasks/new');
  }

  goHome(): void {
    this.router.navigateByUrl('/home');
  }

  goToCategories(): void {
    this.router.navigateByUrl('/personales/categorias');
  }

  completeTask(occurrenceId: number): void {
    this.router.navigate(
      ['/task-occurrences', occurrenceId, 'complete'],
      { queryParams: { returnTo: 'personales' } },
    );
  }

  editTask(taskId: number): void {
    this.router.navigate(
      ['/tasks', taskId, 'edit'],
      { queryParams: { returnTo: 'personales' } },
    );
  }

  deleteTask(task: Task): void {
    const shouldDelete = window.confirm(
      `¿Quieres desactivar la tarea «${task.title}»?`,
    );

    if (!shouldDelete) {
      return;
    }

    this.errorMessage.set(null);

    this.taskService.deleteTask(task.id).subscribe({
      next: () => this.loadTasks(),
      error: () =>
        this.errorMessage.set(
          'No se ha podido eliminar la tarea. Inténtalo de nuevo.',
        ),
    });
  }

  selectCategory(categoryId: number | null): void {
    this.selectedCategoryId.set(categoryId);
  }

  isOccurrenceAvailable(occurrence: TaskOccurrence): boolean {
    return new Date(occurrence.available_from).getTime() <= Date.now();
  }

  private loadTasks(): void {
    this.isLoading.set(true);

    this.taskService
      .getTasks()
      .pipe(
        map((tasks) =>
          tasks.filter((task) => task.is_active && task.household_id === null),
        ),
        switchMap((tasks) => {
          if (tasks.length === 0) {
            return of([] as PersonalTask[]);
          }

          return forkJoin(
            tasks.map((task) =>
              this.taskService.getOccurrences(task.id).pipe(
                map((occurrences) => ({
                  task,
                  nextOccurrence: this.getNextOccurrence(occurrences),
                })),
              ),
            ),
          ).pipe(
            map((personalTasks) =>
              personalTasks.filter(
                (personalTask) =>
                  personalTask.nextOccurrence !== null &&
                  this.isOccurrenceAvailable(personalTask.nextOccurrence),
              ),
            ),
          );
        }),
      )
      .subscribe({
        next: (personalTasks) => {
          this.personalTasks.set(personalTasks);
          this.isLoading.set(false);
        },
        error: () => {
          this.personalTasks.set([]);
          this.isLoading.set(false);
          this.errorMessage.set(
            'No se han podido cargar las tareas personales.',
          );
        },
      });
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

  private getNextOccurrence(
    occurrences: TaskOccurrence[],
  ): TaskOccurrence | null {
    return occurrences[0] ?? null;
  }
}