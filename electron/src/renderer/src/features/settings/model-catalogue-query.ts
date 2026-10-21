import { useQuery } from '@tanstack/react-query';
import { apiJson } from '@/lib/api/client';
import { useBackendStatus } from '@/hooks/use-backend-status';
import { isBackendReachable } from '@shared/utils/backendStage';
import type { ModelLicenseInfo, ModelLicenceAcceptance } from './model-license-contract';

export interface CatalogueModel {
  repo_id: string;
  label: string;
  role: string;
  families?: string[];
  size_gb: number;
  installed: boolean;
  supported: boolean;
  dictation_id?: string;
  required?: boolean;
  curated?: boolean;
  incomplete?: boolean;
  size_on_disk_bytes?: number;
  note?: string;
  gated?: boolean;
  requires_hf_token?: boolean;
  access_url?: string;
  prerequisite_repo_id?: string;
  prerequisite_access_url?: string;
  failure_topic?: string;
  /** Versioned disclosure; absence is unverified, never a permission grant. */
  license_info?: ModelLicenseInfo;
  license_acceptance?: ModelLicenceAcceptance;
  /** Present when the backend is this fork. Missing fields do not block. */
  commercial_ok?: boolean;
  commercial_status?: 'off' | 'allow' | 'conditions' | 'blocked';
  commercial_reason?: string;
  commercial_license?: string;
}

export interface ModelCatalogueResponse {
  commercial_safe?: boolean;
  models: CatalogueModel[];
  total_installed_bytes?: number;
  disk_free_gb?: number;
  /** Free space the backend keeps on top of every model download. */
  disk_headroom_gb?: number;
}

export function useModelCatalogue() {
  const status = useBackendStatus();
  return useQuery({
    queryKey: ['model-catalogue'],
    queryFn: () => apiJson<ModelCatalogueResponse>('/models'),
    staleTime: 30_000,
    enabled: isBackendReachable(status.stage),
  });
}
