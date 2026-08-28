import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { forkJoin, map, of, switchMap } from 'rxjs';

import { HouseholdService } from '../../../core/households/household';
import {
  Household,
  HouseholdMember,
} from '../../../core/households/household.models';
import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';
import { TaskService } from '../../../core/tasks/task.service';
import {
  TaskList,
  TaskListItem,
} from '../../../shared/components/task-list/task-list';

@Component({
  imports: [TaskList],
  selector: 'app-household-detail',
  styleUrl: './household-detail.scss',
  templateUrl: './household-detail.html',
})
export class HouseholdDetail implements OnInit {
  private readonly householdService = inject(HouseholdService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly taskService = inject(TaskService);

  readonly household = signal<Household | null>(null);
  readonly members = signal<HouseholdMember[]>([]);
  readonly taskItems = signal<TaskListItem[]>([]);
  readonly isLoading = signal(true);
  readonly isLoadingTasks = signal(true);
  readonly errorMessage = signal<string | null>(null);
  readonly taskErrorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const householdId = Number(this.route.snapshot.paramMap.get('householdId'));

    if (!Number.isInteger(householdId) || householdId <= 0) {
      this.router.navigateByUrl('/hogares');
      return;
    }

    this.loadHousehold(householdId);
    this.loadTasks(householdId);
  }

  goToHouseholds(): void {
    this.router.navigateByUrl('/hogares');
  }
  
  completeTask(occurrenceId: number): void {
    const householdId = this.household()?.id;

    if (householdId === undefined) {
      return;
    }

    this.router.navigate(
      ['/task-occurrences', occurrenceId, 'complete'],
      { queryParams: { returnTo: 'grupo', householdId } },
    );
  }

  createTask(): void {
    const householdId = this.household()?.id;

    if (householdId === undefined) {
      return;
    }

    this.router.navigate(
      ['/tasks/new'],
      { queryParams: { householdId } },
    );
  }

  private loadHousehold(householdId: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      households: this.householdService.getMyHouseholds(),
      members: this.householdService.getHouseholdMembers(householdId),
    }).subscribe({
      next: ({ households, members }) => {
        const household =
          households.find((item) => item.id === householdId) ?? null;

        if (household === null) {
          this.errorMessage.set('No se ha encontrado el grupo.');
          this.isLoading.set(false);
          return;
        }

        this.household.set(household);
        this.members.set(members);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('No se ha podido cargar el grupo.');
        this.isLoading.set(false);
      },
    });
  }

  private loadTasks(householdId: number): void {
    this.isLoadingTasks.set(true);
    this.taskErrorMessage.set(null);

    this.taskService
      .getTasks()
      .pipe(
        map((tasks) =>
          tasks.filter(
            (task) => task.is_active && task.household_id === householdId,
          ),
        ),
        switchMap((tasks) => {
          if (tasks.length === 0) {
            return of([] as TaskListItem[]);
          }

          return forkJoin(
            tasks.map((task) =>
              this.taskService.getOccurrences(task.id).pipe(
                map((occurrences) => ({
                  task,
                  occurrence: this.getAvailableOccurrence(occurrences),
                })),
              ),
            ),
          ).pipe(
            map((items) =>
              items.filter((item) => item.occurrence !== null),
            ),
          );
        }),
      )
      .subscribe({
        next: (items) => {
          this.taskItems.set(items);
          this.isLoadingTasks.set(false);
        },
        error: () => {
          this.taskItems.set([]);
          this.taskErrorMessage.set(
            'No se han podido cargar las tareas del grupo.',
          );
          this.isLoadingTasks.set(false);
        },
      });
  }

  private getAvailableOccurrence(
    occurrences: TaskOccurrence[],
  ): TaskOccurrence | null {
    return (
      occurrences.find(
        (occurrence) =>
          occurrence.completed_at === null &&
          new Date(occurrence.available_from).getTime() <= Date.now(),
      ) ?? null
    );
  }
}