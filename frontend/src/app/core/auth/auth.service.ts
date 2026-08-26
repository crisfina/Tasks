import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, tap } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import { LoginRequest, TokenRead, UserCreate, UserRead } from './auth.models';
import { SessionService } from './session';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly session = inject(SessionService);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  login(data: LoginRequest): Observable<TokenRead> {
    return this.http.post<TokenRead>(`${this.apiBaseUrl}/auth/login`, data).pipe(
      tap((token) => this.session.saveAccessToken(token.access_token)),
    );
  }

  register(data: UserCreate): Observable<UserRead> {
    return this.http.post<UserRead>(`${this.apiBaseUrl}/auth/register`, data);
  }

  getCurrentUser(): Observable<UserRead> {
    return this.http.get<UserRead>(`${this.apiBaseUrl}/auth/me`);
  }
}