import { Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { HouseholdService } from '../../../core/households/household';
import { Household } from '../../../core/households/household.models';

@Component({
  imports: [],
  selector: 'app-household-list',
  styleUrl: './household-list.scss',
  templateUrl: './household-list.html',
})
export class HouseholdList implements OnInit {
  private readonly householdService = inject(HouseholdService);
  private readonly router = inject(Router);

  readonly households = signal<Household[]>([]);
  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.loadHouseholds();
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

  private loadHouseholds(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.householdService.getMyHouseholds().subscribe({
      next: (households) => {
        this.households.set(households);
        this.isLoading.set(false);
      },
      error: () => {
        this.households.set([]);
        this.errorMessage.set('No se han podido cargar los hogares.');
        this.isLoading.set(false);
      },
    });
  }
}