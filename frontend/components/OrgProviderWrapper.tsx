'use client';

import { OrgProvider } from '@/contexts/OrgContext';

export function OrgProviderWrapper({ children }: { children: React.ReactNode }) {
  return <OrgProvider>{children}</OrgProvider>;
}

