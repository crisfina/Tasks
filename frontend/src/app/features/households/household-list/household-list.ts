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

import { HouseholdService } from '../../../core/households/household';
import { Household } from '../../../core/households/household.models';
import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';
import { TaskService } from '../../../core/tasks/task.service';
import {
  TaskList,
  TaskListItem,
} from '../../../shared/components/task-list/task-list';

interface GroupTask {
  task: Task;
  occurrence: TaskOccurrence;
  contextLabel: string;
}

@Component({
  imports: [TaskList],
  selector: 'app-household-list',
  styleUrl: './household-list.scss',
  templateUrl: './household-list.html',
})
export class HouseholdList implements OnInit {
  private readonly householdService = inject(HouseholdService);
  private readonly taskService = inject(TaskService);
  private readonly router = inject(Router);

  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);
  readonly households = signal<Household[]>([]);
  readonly groupTasks = signal<GroupTask[]>([]);

  readonly groupTaskListItems = computed<TaskListItem[]>(() =>
    this.groupTasks().map((groupTask) => ({
      task: groupTask.task,
      occurrence: groupTask.occurrence,
      contextLabel: `Grupo: ${groupTask.contextLabel}`,
    })),
  );

  ngOnInit(): void {
    this.loadDashboard();
  }

  goHome(): void {
    this.router.navigateByUrl('/home');
  }

  createHousehold(): void {
    this.router.navigateByUrl('/hogares/nuevo');
  }

  openHousehold(householdId: number): void {
    this.router.navigate(['/hogares', householdId]);
  }

  completeTask(occurrenceId: number): void {
    this.router.navigate(
      ['/task-occurrences', occurrenceId, 'complete'],
      { queryParams: { returnTo: 'hogares' } },
    );
  }

  private loadDashboard(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.householdService
      .getMyHouseholds()
      .pipe(
        switchMap((households) => {
          const activeHouseholds = households.filter(
            (household) => household.is_active,
          );

          this.households.set(activeHouseholds);

          const householdNames = new Map(
            activeHouseholds.map((household) => [
              household.id,
              household.name,
            ]),
          );

          return this.taskService.getTasks().pipe(
            map((tasks) =>
              tasks.filter(
                (task) =>
                  task.is_active &&
                  task.household_id !== null &&
                  householdNames.has(task.household_id),
              ),
            ),
            switchMap((tasks) => {
              if (tasks.length === 0) {
                return of([] as GroupTask[]);
              }

              return forkJoin(
                tasks.map((task) =>
                  this.taskService.getOccurrences(task.id).pipe(
                    map((occurrences) => {
                      const occurrence =
                        this.getNextAvailableOccurrence(occurrences);

                      if (occurrence === null) {
                        return null;
                      }

                      return {
                        task,
                        occurrence,
                        contextLabel:
                          householdNames.get(task.household_id!) ??
                          'Grupo',
                      };
                    }),
                  ),
                ),
              ).pipe(
                map((items) =>
                  items.filter(
                    (item): item is GroupTask => item !== null,
                  ),
                ),
              );
            }),
          );
        }),
      )
      .subscribe({
        next: (groupTasks) => {
          this.groupTasks.set(groupTasks);
          this.isLoading.set(false);
        },
        error: () => {
          this.households.set([]);
          this.groupTasks.set([]);
          this.errorMessage.set(
            'No se han podido cargar los grupos y sus tareas.',
          );
          this.isLoading.set(false);
        },
      });
  }

  private getNextAvailableOccurrence(
    occurrences: TaskOccurrence[],
  ): TaskOccurrence | null {
    return (
      occurrences
        .filter(
          (occurrence) =>
            occurrence.completed_at === null &&
            new Date(occurrence.available_from).getTime() <= Date.now(),
        )
        .sort(
          (first, second) =>
            new Date(first.available_from).getTime() -
            new Date(second.available_from).getTime(),
        )[0] ?? null
    );
  }
}