import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { API_BASE_URL } from '../api/api.config';
import { SessionService } from './session';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
  const apiBaseUrl = inject(API_BASE_URL);
  const router = inject(Router);
  const session = inject(SessionService);
  const accessToken = session.getAccessToken();

  if (!accessToken || !request.url.startsWith(apiBaseUrl)) {
    return next(request);
  }

  const authenticatedRequest = request.clone({
    setHeaders: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  return next(authenticatedRequest).pipe(
    catchError((error) => {
      if (error.status === 401) {
        session.clear();
        router.navigateByUrl('/');
      }

      return throwError(() => error);
    }),
  );
};