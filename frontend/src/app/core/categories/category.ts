import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import {
  Category,
  CategoryCreate,
  CategoryUpdate,
} from './category.models';

@Injectable({ providedIn: 'root' })
export class CategoryService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  getPersonalCategories(): Observable<Category[]> {
    return this.http.get<Category[]>(
      `${this.apiBaseUrl}/categories`,
    );
  }

  createPersonalCategory(data: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(
      `${this.apiBaseUrl}/categories`,
      data,
    );
  }

  updatePersonalCategory(
    categoryId: number,
    data: CategoryUpdate,
  ): Observable<Category> {
    return this.http.patch<Category>(
      `${this.apiBaseUrl}/categories/${categoryId}`,
      data,
    );
  }

  deletePersonalCategory(categoryId: number): Observable<void> {
    return this.http.delete<void>(
      `${this.apiBaseUrl}/categories/${categoryId}`,
    );
  }

  getHouseholdCategories(
    householdId: number,
  ): Observable<Category[]> {
    return this.http.get<Category[]>(
      `${this.apiBaseUrl}/households/${householdId}/categories`,
    );
  }

  createHouseholdCategory(
    householdId: number,
    data: CategoryCreate,
  ): Observable<Category> {
    return this.http.post<Category>(
      `${this.apiBaseUrl}/households/${householdId}/categories`,
      data,
    );
  }

  updateHouseholdCategory(
    householdId: number,
    categoryId: number,
    data: CategoryUpdate,
  ): Observable<Category> {
    return this.http.patch<Category>(
      `${this.apiBaseUrl}/households/${householdId}/categories/${categoryId}`,
      data,
    );
  }

  deleteHouseholdCategory(
    householdId: number,
    categoryId: number,
  ): Observable<void> {
    return this.http.delete<void>(
      `${this.apiBaseUrl}/households/${householdId}/categories/${categoryId}`,
    );
  }
}