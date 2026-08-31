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

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-household-organization',
  styleUrl: './household-organization.scss',
  templateUrl: './household-organization.html',
})
export class HouseholdOrganization implements OnInit {
  private readonly categoryService = inject(CategoryService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly roomService = inject(RoomService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly householdId = signal<number | null>(null);
  readonly isLoading = signal(true);
  readonly isSubmittingArea = signal(false);
  readonly isSubmittingCategory = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly areas = signal<Room[]>([]);
  readonly categories = signal<Category[]>([]);

  readonly areaForm = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(100)]],
    color: ['#6d8eeb'],
  });

  readonly categoryForm = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(100)]],
    color: ['#10b981'],
  });

  ngOnInit(): void {
    const householdId = Number(
      this.route.snapshot.paramMap.get('householdId'),
    );

    if (!Number.isInteger(householdId) || householdId <= 0) {
      this.router.navigateByUrl('/hogares');
      return;
    }

    this.householdId.set(householdId);
    this.loadOrganization();
  }

  goToHousehold(): void {
    const householdId = this.householdId();

    if (householdId !== null) {
      this.router.navigateByUrl(`/hogares/${householdId}`);
    }
  }

  createArea(): void {
    const householdId = this.householdId();

    if (householdId === null || this.areaForm.invalid) {
      this.areaForm.markAllAsTouched();
      return;
    }

    this.isSubmittingArea.set(true);
    this.errorMessage.set(null);

    this.roomService
      .createRoom(householdId, this.areaForm.getRawValue())
      .subscribe({
        next: () => {
          this.areaForm.reset({
            name: '',
            color: '#6d8eeb',
          });
          this.isSubmittingArea.set(false);
          this.loadOrganization();
        },
        error: () => {
          this.isSubmittingArea.set(false);
          this.errorMessage.set(
            'No se ha podido crear el área. Inténtalo de nuevo.',
          );
        },
      });
  }

  createCategory(): void {
    const householdId = this.householdId();

    if (householdId === null || this.categoryForm.invalid) {
      this.categoryForm.markAllAsTouched();
      return;
    }

    this.isSubmittingCategory.set(true);
    this.errorMessage.set(null);

    this.categoryService
      .createHouseholdCategory(
        householdId,
        this.categoryForm.getRawValue(),
      )
      .subscribe({
        next: () => {
          this.categoryForm.reset({
            name: '',
            color: '#10b981',
          });
          this.isSubmittingCategory.set(false);
          this.loadOrganization();
        },
        error: () => {
          this.isSubmittingCategory.set(false);
          this.errorMessage.set(
            'No se ha podido crear la categoría. Inténtalo de nuevo.',
          );
        },
      });
  }

  deleteArea(area: Room): void {
    const householdId = this.householdId();

    if (householdId === null) {
      return;
    }

    const shouldDelete = window.confirm(
      `¿Quieres desactivar el área «${area.name}»?`,
    );

    if (!shouldDelete) {
      return;
    }

    this.errorMessage.set(null);

    this.roomService.deleteRoom(householdId, area.id).subscribe({
      next: () => this.loadOrganization(),
      error: () =>
        this.errorMessage.set(
          'No se ha podido eliminar el área. Inténtalo de nuevo.',
        ),
    });
  }

  deleteCategory(category: Category): void {
    const householdId = this.householdId();

    if (householdId === null) {
      return;
    }

    const shouldDelete = window.confirm(
      `¿Quieres desactivar la categoría «${category.name}»?`,
    );

    if (!shouldDelete) {
      return;
    }

    this.errorMessage.set(null);

    this.categoryService
      .deleteHouseholdCategory(householdId, category.id)
      .subscribe({
        next: () => this.loadOrganization(),
        error: () =>
          this.errorMessage.set(
            'No se ha podido eliminar la categoría. Inténtalo de nuevo.',
          ),
      });
  }

  private loadOrganization(): void {
    const householdId = this.householdId();

    if (householdId === null) {
      return;
    }

    this.isLoading.set(true);
    this.errorMessage.set(null);

    forkJoin({
      areas: this.roomService.getHouseholdRooms(householdId),
      categories: this.categoryService.getHouseholdCategories(householdId),
    }).subscribe({
      next: ({ areas, categories }) => {
        this.areas.set(
          areas
            .filter((area) => area.is_active)
            .sort(
              (first, second) =>
                (first.display_order ?? 0) -
                (second.display_order ?? 0),
            ),
        );
        this.categories.set(
          categories
            .filter((category) => category.is_active)
            .sort(
              (first, second) =>
                (first.display_order ?? 0) -
                (second.display_order ?? 0),
            ),
        );
        this.isLoading.set(false);
      },
      error: () => {
        this.areas.set([]);
        this.categories.set([]);
        this.errorMessage.set(
          'No se ha podido cargar la organización del grupo.',
        );
        this.isLoading.set(false);
      },
    });
  }
}