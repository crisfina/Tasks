import { Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';
import { SessionService } from '../../core/auth/session';
import { HouseholdService } from '../../core/households/household';
import {
  Task,
  TaskOccurrence,
} from '../../core/tasks/task.models';
import { TaskService } from '../../core/tasks/task.service';
import { TaskCard } from '../../shared/components/task-card/task-card';
import { TaskList } from '../../shared/components/task-list/task-list';

interface TodayTask {
  task: Task;
  occurrence: TaskOccurrence;
}

@Component({
  imports: [TaskCard],
  selector: 'app-home',
  styleUrl: './home.scss',
  templateUrl: './home.html',
})
export class Home implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly session = inject(SessionService);
  private readonly householdService = inject(HouseholdService);
  private readonly taskService = inject(TaskService);
  private readonly router = inject(Router);

  readonly hasHousehold = signal(false);
  readonly isAdmin = signal(false);
  readonly isLoadingTodayTasks = signal(true);
  readonly errorMessage = signal<string | null>(null);
  readonly todayTasks = signal<TodayTask[]>([]);

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadHouseholds();
    this.loadTodayTasks();
  }

  logout(): void {
    this.session.clear();
    this.router.navigateByUrl('/');
  }

  createPersonalTask(): void {
    this.router.navigateByUrl('/tasks/new');
  }

  goToPersonalTasks(): void {
    this.router.navigateByUrl('/personales');
  }

  goToHouseholds(): void {
    this.router.navigateByUrl('/hogares');
  }

  completeTask(occurrenceId: number): void {
    this.router.navigateByUrl(
      `/task-occurrences/${occurrenceId}/complete`,
    );
  }

  editTask(taskId: number): void {
    this.router.navigate(
      ['/tasks', taskId, 'edit'],
      { queryParams: { returnTo: 'home' } },
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
      next: () => this.loadTodayTasks(),
      error: () =>
        this.errorMessage.set(
          'No se ha podido eliminar la tarea. Inténtalo de nuevo.',
        ),
    });
  }

  private loadCurrentUser(): void {
    this.authService.getCurrentUser().subscribe({
      next: (user) => this.isAdmin.set(user.role === 'admin'),
      error: () => this.isAdmin.set(false),
    });
  }

  private loadHouseholds(): void {
    this.householdService.getMyHouseholds().subscribe({
      next: (households) => this.hasHousehold.set(households.length > 0),
      error: () => this.hasHousehold.set(false),
    });
  }

  private loadTodayTasks(): void {
    const endOfToday = new Date();
    endOfToday.setHours(23, 59, 59, 999);

    this.isLoadingTodayTasks.set(true);

    this.taskService
      .getTasks()
      .pipe(
        map((tasks) =>
          tasks.filter((task) => task.is_active && task.household_id === null),
        ),
        switchMap((tasks) => {
          if (tasks.length === 0) {
            return of([] as TodayTask[]);
          }

          return forkJoin(
            tasks.map((task) =>
              this.taskService.getOccurrences(task.id).pipe(
                map((occurrences) =>
                  occurrences
                    .filter(
                      (occurrence) =>
                        occurrence.completed_at === null &&
                        new Date(occurrence.available_from).getTime() <=
                          endOfToday.getTime(),
                    )
                    .map((occurrence) => ({ task, occurrence })),
                ),
              ),
            ),
          ).pipe(
            map((groups) => {
              const todayTasks = groups.flat();

              return todayTasks.filter(
                (todayTask, index, allTasks) =>
                  allTasks.findIndex(
                    (item) => item.task.id === todayTask.task.id,
                  ) === index,
              );
            }),
          );
        }),
      )
      .subscribe({
        next: (todayTasks) => {
          this.todayTasks.set(todayTasks);
          this.isLoadingTodayTasks.set(false);
        },
        error: () => {
          this.todayTasks.set([]);
          this.errorMessage.set(
            'No se han podido cargar las tareas de hoy.',
          );
          this.isLoadingTodayTasks.set(false);
        },
      });
  }
}