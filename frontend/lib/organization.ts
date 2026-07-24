const ORG_KEY = "todo_organization_id";

export function getOrganizationId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ORG_KEY);
}

export function setOrganizationId(organizationId: string): void {
  localStorage.setItem(ORG_KEY, organizationId);
}

export function clearOrganizationId(): void {
  localStorage.removeItem(ORG_KEY);
}
