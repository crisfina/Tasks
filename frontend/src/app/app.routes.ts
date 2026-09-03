import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';

import { Login } from './features/auth/login/login';
import { Register } from './features/auth/register/register';
import { PersonalCategoryList } from './features/categories/personal-category-list/personal-category-list';
import { Home } from './features/home/home';
import { HouseholdCreate } from './features/households/household-create/household-create';
import { HouseholdList } from './features/households/household-list/household-list';
import { PersonalTaskList } from './features/tasks/personal-task-list/personal-task-list';
import { TaskComplete } from './features/tasks/task-complete/task-complete';
import { TaskCreate } from './features/tasks/task-create/task-create';
import { TaskEdit } from './features/tasks/task-edit/task-edit';
import { HouseholdDetail } from './features/households/household-detail/household-detail';
import { HouseholdOrganization } from './features/households/household-organization/household-organization';
import { TaskOccurrenceEdit } from './features/tasks/task-occurrence-edit/task-occurrence-edit';

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
  { path: 'hogares', component: HouseholdList, canActivate: [authGuard] },
  {
    path: 'hogares/nuevo',
    component: HouseholdCreate,
    canActivate: [authGuard],
  },
  { path: 'tasks/new', component: TaskCreate, canActivate: [authGuard] },
  { path: 'tasks/:taskId/edit', component: TaskEdit, canActivate: [authGuard] },
  {
    path: 'task-occurrences/:occurrenceId/complete',
    component: TaskComplete,
    canActivate: [authGuard],
  },
  {
    path: 'hogares/:householdId',
    component: HouseholdDetail,
    canActivate: [authGuard],
  },
  {
  path: 'hogares/:householdId/organizacion',
    component: HouseholdOrganization,
    canActivate: [authGuard],
  },
  {
  path: 'task-occurrences/:occurrenceId/edit',
    component: TaskOccurrenceEdit,
    canActivate: [authGuard],
  },
  { path: '**', redirectTo: '' },
];