import { provideHttpClient } from '@angular/common/http';
import {ApplicationConfig, provideBrowserGlobalErrorListeners,} from '@angular/core';
import { provideRouter } from '@angular/router';
import { API_BASE_URL } from './core/api/api.config';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(),
    {
      provide: API_BASE_URL,
      useValue: 'http://127.0.0.1:8000',
    },
    provideRouter(routes),
  ],
};