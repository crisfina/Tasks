import { Component, OnInit, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../core/auth/auth.service';
import { SessionService } from '../../core/auth/session';
import { HouseholdService } from '../../core/households/household';

@Component({
  imports: [],
  selector: 'app-home',
  styleUrl: './home.scss',
  templateUrl: './home.html',
})
export class Home implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly session = inject(SessionService);
  private readonly householdService = inject(HouseholdService);
  private readonly router = inject(Router);

  readonly hasHousehold = signal(false);
  readonly isAdmin = signal(false);

  ngOnInit(): void {
    this.loadCurrentUser();
    this.loadHouseholds();
  }

  logout(): void {
    this.session.clear();
    this.router.navigateByUrl('/');
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
}