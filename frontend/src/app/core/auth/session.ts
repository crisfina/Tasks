import { Injectable } from '@angular/core';

const ACCESS_TOKEN_KEY = 'tasks.access-token';

@Injectable({ providedIn: 'root' })
export class SessionService {
  saveAccessToken(accessToken: string): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  clear(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
  }

  hasAccessToken(): boolean {
    return this.getAccessToken() !== null;
  }
}