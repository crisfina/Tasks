import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { Router } from '@angular/router';
import {
  forkJoin,
  map,
  of,
  switchMap,
} from 'rxjs';

import { AuthService } from '../../core/auth/auth.service';
import { SessionService } from '../../core/auth/session';
import { HouseholdService } from '../../core/households/household';
import { TaskList, TaskListItem } from '../../shared/components/task-list/task-list';
import {
  Task,
  TaskOccurrence,
} from '../../core/tasks/task.models';
import { TaskService } from '../../core/tasks/task.service';

interface TodayTask {
  task: Task;
  occurrence: TaskOccurrence;
  contextLabel: string | null;
}

@Component({
  imports: [TaskList],
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

  readonly todayTaskListItems = computed<TaskListItem[]>(() =>
    this.todayTasks().map((todayTask) => ({
      task: todayTask.task,
      occurrence: todayTask.occurrence,
      contextLabel: todayTask.contextLabel,
    })),
  );

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadDashboard();
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
      next: () => this.loadDashboard(),
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

  private loadDashboard(): void {
    const endOfToday = new Date();
    endOfToday.setHours(23, 59, 59, 999);

    this.isLoadingTodayTasks.set(true);

    forkJoin({
      households: this.householdService.getMyHouseholds(),
      tasks: this.taskService.getTasks(),
    })
      .pipe(
        switchMap(({ households, tasks }) => {
          this.hasHousehold.set(households.length > 0);

          const householdNames = new Map(
            households.map((household) => [
              household.id,
              household.name,
            ]),
          );

          const availableTasks = tasks.filter(
            (task) =>
              task.is_active &&
              (
                task.household_id === null ||
                householdNames.has(task.household_id)
              ),
          );

          if (availableTasks.length === 0) {
            return of([] as TodayTask[]);
          }

          return forkJoin(
            availableTasks.map((task) =>
              this.taskService.getOccurrences(task.id).pipe(
                map((occurrences) =>
                  occurrences
                    .filter(
                      (occurrence) =>
                        occurrence.completed_at === null &&
                        new Date(occurrence.available_from).getTime() <=
                          endOfToday.getTime(),
                    )
                    .map((occurrence) => ({
                      task,
                      occurrence,
                      contextLabel:
                        task.household_id === null
                          ? null
                          : `Grupo: ${householdNames.get(task.household_id)}`,
                    })),
                ),
              ),
            ),
          ).pipe(
            map((groups) => groups.flat()),
            map((todayTasks) =>
              todayTasks.filter(
                (todayTask, index, allTasks) =>
                  allTasks.findIndex(
                    (item) => item.task.id === todayTask.task.id,
                  ) === index,
              ),
            ),
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
          this.hasHousehold.set(false);
          this.errorMessage.set(
            'No se han podido cargar las tareas de hoy.',
          );
          this.isLoadingTodayTasks.set(false);
        },
      });
  }
}