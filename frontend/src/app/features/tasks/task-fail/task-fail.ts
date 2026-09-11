import {
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';

import {
  ActivatedRoute,
  Router,
} from '@angular/router';

import {
  map,
  of,
  switchMap,
} from 'rxjs';

import { HouseholdService } from '../../../core/households/household';

import {
  HouseholdMember,
} from '../../../core/households/household.models';

import {
  Task,
  TaskOccurrence,
} from '../../../core/tasks/task.models';

import { TaskService } from '../../../core/tasks/task.service';

interface LoadedTaskFailure {
  occurrence: TaskOccurrence;
  task: Task;
  members: HouseholdMember[];
}

@Component({
  imports: [],
  selector: 'app-task-fail',
  styleUrl: './task-fail.scss',
  templateUrl: './task-fail.html',
})
export class TaskFail implements OnInit {
  private readonly householdService = inject(HouseholdService);

  private readonly route = inject(ActivatedRoute);

  private readonly router = inject(Router);

  private readonly taskService = inject(TaskService);

  readonly occurrence = signal<TaskOccurrence | null>(null);

  readonly task = signal<Task | null>(null);

  readonly members = signal<HouseholdMember[]>([]);

  readonly selectedUserIds = signal<number[]>([]);

  readonly penalize = signal(false);

  readonly isLoading = signal(true);

  readonly isSubmitting = signal(false);

  readonly errorMessage = signal<string | null>(null);

  readonly isGroupTask = computed(() => {
    const task = this.task();

    return task !== null && task.household_id !== null;
  });

  ngOnInit(): void {
    const occurrenceId = Number(
      this.route.snapshot.paramMap.get('occurrenceId'),
    );

    if (!Number.isInteger(occurrenceId) || occurrenceId <= 0) {
      this.goBack();
      return;
    }

    this.loadOccurrence(occurrenceId);
  }

  toggleUser(userId: number): void {
    const selectedUserIds = this.selectedUserIds();

    if (selectedUserIds.includes(userId)) {
      this.selectedUserIds.set(
        selectedUserIds.filter(
          (selectedUserId) => selectedUserId !== userId,
        ),
      );
      return;
    }

    this.selectedUserIds.set([
      ...selectedUserIds,
      userId,
    ]);
  }

  submit(): void {
    const occurrence = this.occurrence();
    const task = this.task();

    if (occurrence === null || task === null) {
      return;
    }

    const isGroupTask = task.household_id !== null;
    const selectedUserIds = this.selectedUserIds();

    if (isGroupTask && selectedUserIds.length === 0) {
      this.errorMessage.set(
        'Selecciona al menos una persona para aplicar la penalización.',
      );
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.taskService
      .failOccurrence(occurrence.id, {
        penalize: isGroupTask || this.penalize(),
        penalized_user_ids: isGroupTask
          ? selectedUserIds
          : [],
      })
      .subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.router.navigateByUrl(this.getReturnUrl());
        },
        error: () => {
          this.isSubmitting.set(false);
          this.errorMessage.set(
            'No se ha podido marcar la tarea como no realizada. Inténtalo de nuevo.',
          );
        },
      });
  }

  cancel(): void {
    this.goBack();
  }

  private loadOccurrence(occurrenceId: number): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.taskService
      .getOccurrence(occurrenceId)
      .pipe(
        switchMap((occurrence) =>
          this.taskService
            .getTask(occurrence.task_id)
            .pipe(
              switchMap((task) => {
                if (task.household_id === null) {
                  return of<LoadedTaskFailure>({
                    occurrence,
                    task,
                    members: [],
                  });
                }

                return this.householdService
                  .getHouseholdMembers(task.household_id)
                  .pipe(
                    map(
                      (members): LoadedTaskFailure => ({
                        occurrence,
                        task,
                        members,
                      }),
                    ),
                  );
              }),
            ),
        ),
      )
      .subscribe({
        next: ({ occurrence, task, members }) => {
          this.occurrence.set(occurrence);
          this.task.set(task);
          this.members.set(members);

          if (
            occurrence.assigned_user_id !== null &&
            members.some(
              (member) =>
                member.user_id === occurrence.assigned_user_id,
            )
          ) {
            this.selectedUserIds.set([
              occurrence.assigned_user_id,
            ]);
          }

          this.isLoading.set(false);
        },
        error: () => {
          this.errorMessage.set(
            'No se ha podido cargar la tarea.',
          );
          this.isLoading.set(false);
        },
      });
  }

  private goBack(): void {
    this.router.navigateByUrl(this.getReturnUrl());
  }

  private getReturnUrl(): string {
    const returnTo = this.route.snapshot.queryParamMap.get(
      'returnTo',
    );

    if (returnTo === 'personales') {
      return '/personales';
    }

    if (returnTo === 'hogares') {
      return '/hogares';
    }

    if (returnTo === 'grupo') {
      const householdId = Number(
        this.route.snapshot.queryParamMap.get('householdId'),
      );

      if (
        Number.isInteger(householdId) &&
        householdId > 0
      ) {
        return `/hogares/${householdId}`;
      }
    }

    return '/home';
  }
}