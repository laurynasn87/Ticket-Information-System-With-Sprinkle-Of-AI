import { TestBed } from '@angular/core/testing';

import { RoleAuthGuard } from './roleAuth.guard';

describe('roleAuthGuard', () => {
  let guard: RoleAuthGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(RoleAuthGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
