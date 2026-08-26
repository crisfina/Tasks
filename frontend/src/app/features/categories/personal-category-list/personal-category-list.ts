import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { Category } from '../../../core/categories/category.models';
import { CategoryService } from '../../../core/categories/category';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-personal-category-list',
  styleUrl: './personal-category-list.scss',
  templateUrl: './personal-category-list.html',
})
export class PersonalCategoryList implements OnInit {
  private readonly categoryService = inject(CategoryService);
  private readonly formBuilder = inject(FormBuilder);
  private readonly router = inject(Router);

  readonly isLoading = signal(true);
  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);
  readonly categories = signal<Category[]>([]);

  readonly categoryForm = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(100)]],
    color: ['#FFFFFF'],
  });

  ngOnInit(): void {
    this.loadCategories();
  }

  goToPersonalTasks(): void {
    this.router.navigateByUrl('/personales');
  }

  createCategory(): void {
    if (this.categoryForm.invalid) {
      this.categoryForm.markAllAsTouched();
      return;
    }

    const formValue = this.categoryForm.getRawValue();

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    this.categoryService
      .createPersonalCategory({
        name: formValue.name,
        color: formValue.color,
      })
      .subscribe({
        next: () => {
          this.categoryForm.reset({
            name: '',
            color: '#FFFFFF',
          });
          this.isSubmitting.set(false);
          this.loadCategories();
        },
        error: () => {
          this.isSubmitting.set(false);
          this.errorMessage.set(
            'No se ha podido crear la categoría. Inténtalo de nuevo.',
          );
        },
      });
  }

  deleteCategory(category: Category): void {
    const shouldDelete = window.confirm(
      `¿Quieres eliminar la categoría «${category.name}»?`,
    );

    if (!shouldDelete) {
      return;
    }

    this.errorMessage.set(null);

    this.categoryService.deletePersonalCategory(category.id).subscribe({
      next: () => this.loadCategories(),
      error: () =>
        this.errorMessage.set(
          'No se ha podido eliminar la categoría. Inténtalo de nuevo.',
        ),
    });
  }

  private loadCategories(): void {
    this.isLoading.set(true);

    this.categoryService.getPersonalCategories().subscribe({
      next: (categories) => {
        this.categories.set(
          categories
            .filter((category) => category.is_active)
            .sort(
              (first, second) =>
                (first.display_order ?? 0) - (second.display_order ?? 0),
            ),
        );
        this.isLoading.set(false);
      },
      error: () => {
        this.categories.set([]);
        this.errorMessage.set(
          'No se han podido cargar las categorías personales.',
        );
        this.isLoading.set(false);
      },
    });
  }
}