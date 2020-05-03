export interface IUserProfile {
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  username: string;
  id: number;
}

export interface IUserProfileUpdate {
  email?: string;
  username?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IUserProfileCreate {
  email: string;
  username?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IAppNotification {
  content: string;
  color?: string;
  showProgress?: boolean;
}
