import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { HouseholdService } from '../../../core/households/household';

@Component({
  imports: [ReactiveFormsModule],
  selector: 'app-household-create',
  styleUrl: './household-create.scss',
  templateUrl: './household-create.html',
})
export class HouseholdCreate {
  private readonly formBuilder = inject(FormBuilder);
  private readonly householdService = inject(HouseholdService);
  private readonly router = inject(Router);

  readonly isSubmitting = signal(false);
  readonly errorMessage = signal<string | null>(null);

  readonly householdForm = this.formBuilder.nonNullable.group({
    name: ['', [Validators.required, Validators.maxLength(100)]],
  });

  submit(): void {
    if (this.householdForm.invalid) {
      this.householdForm.markAllAsTouched();
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    const { name } = this.householdForm.getRawValue();

    this.householdService.createHousehold({ name: name.trim() }).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.router.navigateByUrl('/hogares');
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set(
          'No se ha podido crear el grupo. Inténtalo de nuevo.',
        );
      },
    });
  }

  cancel(): void {
    this.router.navigateByUrl('/hogares');
  }
}