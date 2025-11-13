'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { orgApi } from '@/lib/api';
import { Organization } from '@/types/organization';

interface OrgContextType {
  organizations: Organization[];
  currentOrg: Organization | null;
  setCurrentOrg: (org: Organization | null) => void;
  refreshOrgs: () => Promise<void>;
  loading: boolean;
}

const OrgContext = createContext<OrgContextType | undefined>(undefined);

export function OrgProvider({ children }: { children: ReactNode }) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [currentOrg, setCurrentOrgState] = useState<Organization | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshOrgs = async () => {
    try {
      const orgs = await orgApi.listMine();
      setOrganizations(orgs);
      
      // Restore last used org from localStorage or use first org
      if (orgs.length > 0) {
        const lastOrgId = localStorage.getItem('currentOrgId');
        const lastOrg = orgs.find(o => o.id === parseInt(lastOrgId || '0'));
        setCurrentOrgState(lastOrg || orgs[0]);
      } else {
        setCurrentOrgState(null);
      }
    } catch (error) {
      console.error('Failed to load organizations:', error);
      setOrganizations([]);
      setCurrentOrgState(null);
    } finally {
      setLoading(false);
    }
  };

  const setCurrentOrg = (org: Organization | null) => {
    setCurrentOrgState(org);
    if (org) {
      localStorage.setItem('currentOrgId', org.id.toString());
    } else {
      localStorage.removeItem('currentOrgId');
    }
  };

  useEffect(() => {
    refreshOrgs();
  }, []);

  return (
    <OrgContext.Provider
      value={{
        organizations,
        currentOrg,
        setCurrentOrg,
        refreshOrgs,
        loading,
      }}
    >
      {children}
    </OrgContext.Provider>
  );
}

export function useOrg() {
  const context = useContext(OrgContext);
  if (context === undefined) {
    throw new Error('useOrg must be used within an OrgProvider');
  }
  return context;
}

