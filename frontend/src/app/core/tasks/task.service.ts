import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import {
  Task,
  TaskCreate,
  TaskOccurrence,
  TaskOccurrenceComplete,
  TaskOccurrenceCreate,
  TaskUpdate,
} from './task.models';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);
  private readonly apiBaseUrl = inject(API_BASE_URL);

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(`${this.apiBaseUrl}/tasks`);
  }

  getTask(taskId: number): Observable<Task> {
    return this.http.get<Task>(`${this.apiBaseUrl}/tasks/${taskId}`);
  }

  createTask(data: TaskCreate): Observable<Task> {
    return this.http.post<Task>(`${this.apiBaseUrl}/tasks`, data);
  }

  updateTask(taskId: number, data: TaskUpdate): Observable<Task> {
    return this.http.patch<Task>(
      `${this.apiBaseUrl}/tasks/${taskId}`,
      data,
    );
  }

  deleteTask(taskId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiBaseUrl}/tasks/${taskId}`);
  }

  getOccurrences(taskId: number): Observable<TaskOccurrence[]> {
    return this.http.get<TaskOccurrence[]>(
      `${this.apiBaseUrl}/tasks/${taskId}/occurrences`,
    );
  }

  createOccurrence(
    taskId: number,
    data: TaskOccurrenceCreate,
  ): Observable<TaskOccurrence> {
    return this.http.post<TaskOccurrence>(
      `${this.apiBaseUrl}/tasks/${taskId}/occurrences`,
      data,
    );
  }

  completeOccurrence(
    occurrenceId: number,
    data: TaskOccurrenceComplete,
  ): Observable<TaskOccurrence> {
    return this.http.post<TaskOccurrence>(
      `${this.apiBaseUrl}/task-occurrences/${occurrenceId}/complete`,
      data,
    );
  }
}