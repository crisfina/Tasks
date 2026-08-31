import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import {
  Household,
  HouseholdCreate,
  HouseholdInvitationAccept,
  HouseholdInvitationCreated,
  HouseholdInvitationCreate,
  HouseholdMember,
} from './household.models';

@Injectable({ providedIn: 'root' })
export class HouseholdService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  getMyHouseholds(): Observable<Household[]> {
    return this.http.get<Household[]>(
      `${this.apiBaseUrl}/households`,
    );
  }

  createHousehold(data: HouseholdCreate): Observable<Household> {
    return this.http.post<Household>(
      `${this.apiBaseUrl}/households`,
      data,
    );
  }

  getHouseholdMembers(
    householdId: number,
  ): Observable<HouseholdMember[]> {
    return this.http.get<HouseholdMember[]>(
      `${this.apiBaseUrl}/households/${householdId}/members`,
    );
  }

  createHouseholdInvitation(
    householdId: number,
    data: HouseholdInvitationCreate,
  ): Observable<HouseholdInvitationCreated> {
    return this.http.post<HouseholdInvitationCreated>(
      `${this.apiBaseUrl}/households/${householdId}/invitations`,
      data,
    );
  }

  acceptHouseholdInvitation(
    data: HouseholdInvitationAccept,
  ): Observable<HouseholdMember> {
    return this.http.post<HouseholdMember>(
      `${this.apiBaseUrl}/households/invitations/accept`,
      data,
    );
  }
}