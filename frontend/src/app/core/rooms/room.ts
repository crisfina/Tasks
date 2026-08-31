import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import {
  Room,
  RoomCreate,
  RoomUpdate,
} from './room.models';

@Injectable({ providedIn: 'root' })
export class RoomService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  getHouseholdRooms(householdId: number): Observable<Room[]> {
    return this.http.get<Room[]>(
      `${this.apiBaseUrl}/households/${householdId}/rooms`,
    );
  }

  createRoom(
    householdId: number,
    data: RoomCreate,
  ): Observable<Room> {
    return this.http.post<Room>(
      `${this.apiBaseUrl}/households/${householdId}/rooms`,
      data,
    );
  }

  updateRoom(
    householdId: number,
    roomId: number,
    data: RoomUpdate,
  ): Observable<Room> {
    return this.http.patch<Room>(
      `${this.apiBaseUrl}/households/${householdId}/rooms/${roomId}`,
      data,
    );
  }

  deleteRoom(
    householdId: number,
    roomId: number,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiBaseUrl}/households/${householdId}/rooms/${roomId}`,
    );
  }

  restoreRoom(
    householdId: number,
    roomId: number,
  ): Observable<Room> {
    return this.http.post<Room>(
      `${this.apiBaseUrl}/households/${householdId}/rooms/${roomId}/restore`,
      {},
    );
  }
}