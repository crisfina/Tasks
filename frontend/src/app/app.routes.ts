import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';
import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { PersonalCategoryList } from './features/categories/personal-category-list/personal-category-list';
import { Home } from './features/home/home';
import { PersonalTaskList } from './features/tasks/personal-task-list/personal-task-list';
import { TaskComplete } from './features/tasks/task-complete/task-complete';
import { TaskCreate } from './features/tasks/task-create/task-create';
import { TaskEdit } from './features/tasks/task-edit/task-edit';

export const routes: Routes = [
  { path: '', component: Login },
  { path: 'register', component: Register },
  { path: 'home', component: Home, canActivate: [authGuard] },
  { path: 'personales', component: PersonalTaskList, canActivate: [authGuard] },
  {
    path: 'personales/categorias',
    component: PersonalCategoryList,
    canActivate: [authGuard],
  },
  { path: 'tasks/new', component: TaskCreate, canActivate: [authGuard] },
  { path: 'tasks/:taskId/edit', component: TaskEdit, canActivate: [authGuard] },
  {
    path: 'task-occurrences/:occurrenceId/complete',
    component: TaskComplete,
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: '' },
];