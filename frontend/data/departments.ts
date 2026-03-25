/**
 * Department types and utilities for the departments data table.
 */

export interface Department {
  code: string;
  name: string;
  region: string;
  enterprises: number;
  growth: number;
  score: number;
  dynamism: string;
  territory: string;
}

export const REGIONS = [
  'Auvergne-Rhone-Alpes',
  'Bourgogne-Franche-Comte',
  'Bretagne',
  'Centre-Val de Loire',
  'Corse',
  'Grand Est',
  'Hauts-de-France',
  'Ile-de-France',
  'Normandie',
  'Nouvelle-Aquitaine',
  'Occitanie',
  'Pays de la Loire',
  "Provence-Alpes-Cote d'Azur",
  'Guadeloupe',
  'Martinique',
  'Guyane',
  'La Reunion',
  'Mayotte',
] as const;

export function formatEnterprises(count: number): string {
  if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`;
  if (count >= 1000) return `${(count / 1000).toFixed(1)}k`;
  return count.toString();
}
