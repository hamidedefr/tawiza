'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/layout';
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
  GlassCardTitle,
  GlassCardDescription,
} from '@/components/ui/glass-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  Search,
  AlertTriangle,
  BarChart3,
  MapPin,
  Calendar,
  Database,
  Loader2,
  ArrowRight,
  Activity,
  TrendingUp,
  Shield,
  Brain,
  FileText,
  Building2,
  X,
  GitBranch,
  Globe,
  Maximize,
  Minimize2,
} from 'lucide-react';
import { useRelations } from '@/hooks/use-relations';
import RelationGraphEnhanced from '@/components/dashboard/investigation/RelationGraphEnhanced';
import CoverageBar from '@/components/dashboard/investigation/CoverageBar';
import GapsPanel from '@/components/dashboard/investigation/GapsPanel';
import WhatIfPanel from '@/components/dashboard/investigation/WhatIfPanel';
import NetworkAnalyticsPanel from '@/components/dashboard/investigation/NetworkAnalyticsPanel';
import EcosystemScorePanel from '@/components/dashboard/investigation/EcosystemScorePanel';
import NodeDetailPanel from '@/components/dashboard/investigation/NodeDetailPanel';
import GraphFilters from '@/components/dashboard/investigation/GraphFilters';
import type { ColorMode } from '@/components/dashboard/investigation/GraphFilters';
import type { GraphNode } from '@/types/relations';

const API = process.env.NEXT_PUBLIC_API_URL || '';

// ── Types ────────────────────────────────────────────────────
interface SearchResult {
  signal_id: number;
  source: string;
  department: string | null;
  date: string | null;
  metric: string;
  value: number | null;
  type: string | null;
  text: string;
  collected_at: string | null;
}

interface EntityProfile {
  identifier: string;
  signal_count: number;
  sources: string[];
  departments: string[];
  first_seen: string | null;
  last_seen: string | null;
  risk_level: string;
  risk_indicators: { type: string; date: string | null; source: string; detail: string }[];
  signals: SearchResult[];
}

interface DeptOverview {
  department: string;
  signal_breakdown: { type: string; count: number }[];
  risk_signals: { id: number; source: string; type: string; date: string | null; text: string }[];
  micro_signals: { id: number; type: string; score: number; description: string }[];
  monthly_trend: { month: string; total: number; risk_count: number }[];
}

interface LLMAnalysis {
  identifier: string;
  signal_count: number;
  analysis: string;
}

// ── Helpers ──────────────────────────────────────────────────
const sourceColors: Record<string, string> = {
  bodacc: 'bg-red-500/15 text-red-400 border-red-500/25',
  france_travail: 'bg-blue-500/15 text-blue-400 border-blue-500/25',
  sirene: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  insee: 'bg-sky-500/15 text-sky-400 border-sky-500/25',
  dvf: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  sitadel: 'bg-violet-500/15 text-violet-400 border-violet-500/25',
  presse_locale: 'bg-pink-500/15 text-pink-400 border-pink-500/25',
};

const riskColors: Record<string, string> = {
  high: 'bg-red-500/15 text-red-400 border-red-500/25',
  medium: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
  low: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
};

function formatDate(d: string | null): string {
  if (!d) return '-';
  try {
    return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch {
    return d;
  }
}

// ── Main Page ────────────────────────────────────────────────
export default function InvestigationPage() {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [entity, setEntity] = useState<EntityProfile | null>(null);
  const [deptOverview, setDeptOverview] = useState<DeptOverview | null>(null);
  const [llmAnalysis, setLlmAnalysis] = useState<LLMAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState<'search' | 'entity' | 'department' | 'relations'>('search');
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  // ── Relations tab state ──
  const [relationsDept, setRelationsDept] = useState('');
  const [confidenceFilter, setConfidenceFilter] = useState(40);
  const [showGaps, setShowGaps] = useState(false);
  const [showWhatIf, setShowWhatIf] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showEcosystem, setShowEcosystem] = useState(false);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const ALL_TYPES = ['enterprise', 'territory', 'institution', 'sector', 'association', 'formation', 'financial', 'competitiveness_pole', 'cluster', 'incubator', 'dev_agency', 'research_lab', 'employment_basin', 'collectivity', 'economic_zone', 'professional_network'];
  const ALL_LEVELS = ['structural', 'inferred', 'hypothetical'];
  const [enabledTypes, setEnabledTypes] = useState<Set<string>>(new Set(ALL_TYPES));
  const [enabledLevels, setEnabledLevels] = useState<Set<string>>(new Set(ALL_LEVELS));
  const [graphSearch, setGraphSearch] = useState('');
  const [selectedCommunity, setSelectedCommunity] = useState<number | null>(null);
  const [colorMode, setColorMode] = useState<ColorMode>('type');
  const [graphFullscreen, setGraphFullscreen] = useState(false);
  const {
    graph, coverage, gaps, whatIfResult, analytics, ecosystemScore,
    loading: relLoading, discovering, simulating,
    fetchGraph, fetchCoverage, fetchGaps, discover, whatif, exportGraph, fetchAnalytics, fetchEcosystemScore,
  } = useRelations(relationsDept || null);

  // Escape key exits fullscreen
  useEffect(() => {
    if (!graphFullscreen) return;
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setGraphFullscreen(false);
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [graphFullscreen]);

  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) return;
    setLoading(true);
    setEntity(null);
    setDeptOverview(null);
    setLlmAnalysis(null);
    try {
      const res = await fetch(`${API}/api/v1/investigation/search?q=${encodeURIComponent(q)}&limit=30`);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        setActiveTab('search');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadEntity = useCallback(async (identifier: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/investigation/entity/${encodeURIComponent(identifier)}`);
      if (res.ok) {
        setEntity(await res.json());
        setActiveTab('entity');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadDeptOverview = useCallback(async (dept: string) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v1/investigation/department/${dept}/overview?days=90`);
      if (res.ok) {
        setDeptOverview(await res.json());
        setActiveTab('department');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  const runLLMAnalysis = useCallback(async (identifier: string) => {
    setAnalyzing(true);
    setLlmAnalysis(null);
    try {
      const res = await fetch(`${API}/api/v1/investigation/analyze?identifier=${encodeURIComponent(identifier)}`, {
        method: 'POST',
      });
      if (res.ok) {
        setLlmAnalysis(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAnalyzing(false);
    }
  }, []);

  const handleSearch = (value: string) => {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(value), 400);
  };

  return (
    <DashboardLayout
      title="Investigation"
      description="Recherche approfondie dans les signaux territoriaux"
    >
      <div className="space-y-6">
        {/* Search Bar */}
        <GlassCard>
          <GlassCardContent className="p-4">
            <div className="flex items-center gap-3">
              <Search className="w-5 h-5 text-muted-foreground shrink-0" />
              <Input
                placeholder="Rechercher par SIREN, nom d&#39;entreprise, departement, mot-cle..."
                value={query}
                onChange={(e) => handleSearch(e.target.value)}
                className="border-0 bg-transparent text-base focus-visible:ring-0 focus-visible:ring-offset-0"
              />
              {loading && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />}
              {query && (
                <Button variant="ghost" size="icon" onClick={() => { setQuery(''); setResults([]); }}>
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
            {/* Quick department buttons */}
            <div className="flex flex-wrap gap-2 mt-3">
              {['75', '13', '69', '33', '31', '59', '06', '34', '44', '67'].map((d) => (
                <Button
                  key={d}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => loadDeptOverview(d)}
                >
                  <MapPin className="w-3 h-3 mr-1" />
                  Dept {d}
                </Button>
              ))}
            </div>
          </GlassCardContent>
        </GlassCard>

        {/* Tab Navigation */}
        <div className="flex gap-1 p-1 rounded-xl bg-muted/30 border border-border">
          <button
            onClick={() => setActiveTab('search')}
            className={cn(
              'flex-1 min-w-[80px] px-3 py-2 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5',
              activeTab === 'search'
                ? 'bg-primary/15 text-primary border border-primary/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            )}
          >
            <Search className="w-3.5 h-3.5" />
            Recherche
          </button>
          <button
            onClick={() => setActiveTab('entity')}
            className={cn(
              'flex-1 min-w-[80px] px-3 py-2 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5',
              activeTab === 'entity'
                ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            )}
          >
            <Building2 className="w-3.5 h-3.5" />
            Entite
          </button>
          <button
            onClick={() => setActiveTab('department')}
            className={cn(
              'flex-1 min-w-[80px] px-3 py-2 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5',
              activeTab === 'department'
                ? 'bg-sky-500/15 text-sky-400 border border-sky-500/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            )}
          >
            <MapPin className="w-3.5 h-3.5" />
            Departement
          </button>
          <button
            onClick={() => setActiveTab('relations')}
            className={cn(
              'flex-1 min-w-[80px] px-3 py-2 text-xs sm:text-sm font-medium rounded-lg transition-all flex items-center justify-center gap-1.5',
              activeTab === 'relations'
                ? 'bg-violet-500/15 text-violet-400 border border-violet-500/20'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
            )}
          >
            <GitBranch className="w-3.5 h-3.5" />
            Relations
          </button>
        </div>

        {/* Search Results */}
        {activeTab === 'search' && results.length > 0 && (
          <GlassCard>
            <GlassCardHeader>
              <GlassCardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                {results.length} resultats
              </GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <div className="space-y-2">
                {results.map((r) => (
                  <div
                    key={r.signal_id}
                    className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/30 transition-colors cursor-pointer group"
                    onClick={() => r.department && loadDeptOverview(r.department)}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap mb-1">
                        <Badge variant="outline" className={cn('text-[10px]', sourceColors[r.source] || '')}>
                          {r.source}
                        </Badge>
                        {r.department && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <MapPin className="w-3 h-3" /> {r.department}
                          </span>
                        )}
                        {r.date && (
                          <span className="flex items-center gap-1 text-xs text-muted-foreground">
                            <Calendar className="w-3 h-3" /> {formatDate(r.date)}
                          </span>
                        )}
                        {r.type && (
                          <Badge variant="outline" className="text-[10px] bg-muted/50">
                            {r.type}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-foreground line-clamp-2">
                        {r.text || r.metric}
                      </p>
                      {r.value != null && (
                        <span className="text-xs text-muted-foreground mt-1 inline-flex items-center gap-1">
                          <Database className="w-3 h-3" /> {r.metric} = {r.value}
                        </span>
                      )}
                    </div>
                    <ArrowRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0 mt-1" />
                  </div>
                ))}
              </div>
            </GlassCardContent>
          </GlassCard>
        )}

        {/* Department Overview */}
        {activeTab === 'department' && deptOverview && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <h2 className="text-lg font-semibold">Departement {deptOverview.department}</h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => router.push(`/dashboard/departments/${deptOverview.department}`)}
              >
                Voir la fiche
                <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => runLLMAnalysis(deptOverview.department)}
                disabled={analyzing}
              >
                {analyzing ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Brain className="w-3.5 h-3.5 mr-1" />}
                Analyser avec TAJINE
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Signal Breakdown */}
              <GlassCard>
                <GlassCardHeader>
                  <GlassCardTitle className="text-sm flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" /> Repartition
                  </GlassCardTitle>
                </GlassCardHeader>
                <GlassCardContent>
                  <div className="space-y-2">
                    {deptOverview.signal_breakdown.map((s) => (
                      <div key={s.type} className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground truncate">{s.type || 'autre'}</span>
                        <span className="font-medium">{s.count}</span>
                      </div>
                    ))}
                  </div>
                </GlassCardContent>
              </GlassCard>

              {/* Risk Signals */}
              <GlassCard>
                <GlassCardHeader>
                  <GlassCardTitle className="text-sm flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-[var(--error)]" /> Signaux a risque ({deptOverview.risk_signals.length})
                  </GlassCardTitle>
                </GlassCardHeader>
                <GlassCardContent>
                  {deptOverview.risk_signals.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-4">Aucun signal a risque</p>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {deptOverview.risk_signals.map((r) => (
                        <div key={r.id} className="p-2 bg-red-500/5 rounded border border-red-500/10 text-xs">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-[9px] bg-red-500/10 text-red-400">{r.type}</Badge>
                            <span className="text-muted-foreground">{formatDate(r.date)}</span>
                          </div>
                          <p className="text-muted-foreground line-clamp-2">{r.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </GlassCardContent>
              </GlassCard>

              {/* Micro-signals */}
              <GlassCard>
                <GlassCardHeader>
                  <GlassCardTitle className="text-sm flex items-center gap-2">
                    <Activity className="w-4 h-4 text-[var(--warning)]" /> Micro-signaux ({deptOverview.micro_signals.length})
                  </GlassCardTitle>
                </GlassCardHeader>
                <GlassCardContent>
                  {deptOverview.micro_signals.length === 0 ? (
                    <p className="text-xs text-muted-foreground text-center py-4">Aucun micro-signal</p>
                  ) : (
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {deptOverview.micro_signals.map((m) => (
                        <div key={m.id} className="p-2 bg-muted/30 rounded text-xs">
                          <div className="flex items-center justify-between mb-1">
                            <Badge variant="outline" className="text-[9px]">{m.type}</Badge>
                            <span className={cn(
                              'text-[10px] font-mono font-medium',
                              m.score >= 0.8 ? 'text-red-400' : m.score >= 0.5 ? 'text-amber-400' : 'text-emerald-400'
                            )}>
                              {(m.score * 100).toFixed(0)}%
                            </span>
                          </div>
                          <p className="text-muted-foreground line-clamp-2">{m.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </GlassCardContent>
              </GlassCard>
            </div>

            {/* LLM Analysis */}
            {llmAnalysis && (
              <GlassCard>
                <GlassCardHeader>
                  <GlassCardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5 text-primary" /> Analyse TAJINE
                  </GlassCardTitle>
                  <GlassCardDescription>
                    Basee sur {llmAnalysis.signal_count} signaux
                  </GlassCardDescription>
                </GlassCardHeader>
                <GlassCardContent>
                  <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap">
                    {llmAnalysis.analysis}
                  </div>
                </GlassCardContent>
              </GlassCard>
            )}
            {analyzing && (
              <GlassCard>
                <GlassCardContent className="flex items-center justify-center gap-3 py-12">
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  <span className="text-sm text-muted-foreground">Analyse en cours avec TAJINE (qwen3:32b)...</span>
                </GlassCardContent>
              </GlassCard>
            )}
          </div>
        )}

        {/* Relations Tab */}
        {activeTab === 'relations' && (
          <div className="space-y-4">
            {/* Search bar + discover button */}
            <GlassCard>
              <GlassCardContent className="p-3">
                <div className="flex flex-col sm:flex-row gap-2">
                  <Input
                    type="text"
                    placeholder="Code departement (ex: 13, 75, 59...)"
                    value={relationsDept === 'all' ? '' : relationsDept}
                    onChange={(e) => setRelationsDept(e.target.value.trim())}
                    className="flex-1 bg-transparent border-border text-sm focus-visible:ring-violet-500/30"
                    disabled={relationsDept === 'all'}
                  />
                  <Button
                    onClick={() => {
                      if (relationsDept === 'all') {
                        setRelationsDept('');
                      } else {
                        setRelationsDept('all');
                      }
                    }}
                    variant="outline"
                    className={cn(
                      'border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10',
                      relationsDept === 'all' && 'bg-cyan-500/20 border-cyan-400/50',
                    )}
                  >
                    <Globe className="w-3.5 h-3.5 mr-1.5" />
                    {relationsDept === 'all' ? 'Tous (actif)' : 'Tous'}
                  </Button>
                  <Button
                    onClick={() => fetchGraph(confidenceFilter / 100)}
                    disabled={!relationsDept || relLoading}
                    variant="outline"
                    className="border-sky-500/30 text-sky-400 hover:bg-sky-500/10"
                  >
                    {relLoading ? (
                      <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                    ) : (
                      <Database className="w-3.5 h-3.5 mr-1.5" />
                    )}
                    Charger
                  </Button>
                  <Button
                    onClick={() => discover()}
                    disabled={!relationsDept || relationsDept === 'all' || discovering}
                    variant="outline"
                    className="border-violet-500/30 text-violet-400 hover:bg-violet-500/10"
                  >
                    {discovering ? (
                      <>
                        <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                        Decouverte...
                      </>
                    ) : (
                      <>
                        <GitBranch className="w-3.5 h-3.5 mr-1.5" />
                        Decouvrir
                      </>
                    )}
                  </Button>
                </div>
              </GlassCardContent>
            </GlassCard>

            {/* Confidence slider + panel toggles */}
            {graph && graph.nodes.length > 0 && (
              <GlassCard>
                <GlassCardContent className="p-3">
                  <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                    <div className="flex items-center gap-2 flex-1 w-full">
                      <span className="text-xs text-muted-foreground whitespace-nowrap">Confiance min:</span>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={confidenceFilter}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          setConfidenceFilter(val);
                          fetchGraph(val / 100);
                        }}
                        className="flex-1 accent-violet-500"
                      />
                      <span className="text-xs text-muted-foreground font-mono w-8 text-right">{confidenceFilter}%</span>
                      {graph && (
                        <span className="text-[10px] text-muted-foreground whitespace-nowrap ml-2">
                          {graph.nodes.length} noeuds, {graph.links.length} liens
                          {graph.total_relations_unfiltered && graph.total_relations_unfiltered > graph.links.length
                            ? ` / ${graph.total_relations_unfiltered}`
                            : ''}
                        </span>
                      )}
                    </div>
                    <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={showGaps}
                        onChange={(e) => {
                          setShowGaps(e.target.checked);
                          if (e.target.checked && !gaps) fetchGaps();
                        }}
                        className="accent-amber-500"
                      />
                      Lacunes
                    </label>
                    <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={showWhatIf}
                        onChange={(e) => setShowWhatIf(e.target.checked)}
                        className="accent-red-500"
                      />
                      What-If
                    </label>
                    <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={showAnalytics}
                        onChange={(e) => {
                          setShowAnalytics(e.target.checked);
                          if (e.target.checked && !analytics) fetchAnalytics();
                        }}
                        className="accent-emerald-500"
                      />
                      Analytics
                    </label>
                    <label className="flex items-center gap-2 text-xs text-muted-foreground cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={showEcosystem}
                        onChange={(e) => {
                          setShowEcosystem(e.target.checked);
                          if (e.target.checked && !ecosystemScore) fetchEcosystemScore();
                        }}
                        className="accent-sky-500"
                      />
                      Ecosysteme
                    </label>
                  </div>
                </GlassCardContent>
              </GlassCard>
            )}

            {/* Graph filters bar */}
            {graph && graph.nodes.length > 0 && (
              <GraphFilters
                actorTypes={ALL_TYPES}
                enabledTypes={enabledTypes}
                onToggleType={(t) => {
                  setEnabledTypes((prev) => {
                    const next = new Set(prev);
                    if (next.has(t)) next.delete(t);
                    else next.add(t);
                    return next;
                  });
                }}
                enabledLevels={enabledLevels}
                onToggleLevel={(l) => {
                  setEnabledLevels((prev) => {
                    const next = new Set(prev);
                    if (next.has(l)) next.delete(l);
                    else next.add(l);
                    return next;
                  });
                }}
                searchQuery={graphSearch}
                onSearchChange={setGraphSearch}
                communities={analytics?.communities?.map((c) => ({ id: c.id, size: c.size })) || []}
                selectedCommunity={selectedCommunity}
                onSelectCommunity={setSelectedCommunity}
                colorMode={colorMode}
                onColorModeChange={(m) => {
                  setColorMode(m);
                  if (!analytics) fetchAnalytics();
                }}
              />
            )}

            {/* Coverage bar */}
            <CoverageBar coverage={coverage} isLoading={relLoading} />

            {/* Graph + NodeDetailPanel */}
            <div className={cn(
              'relative',
              graphFullscreen && 'fixed inset-0 z-50 bg-background/95 backdrop-blur-sm',
            )}>
              {graphFullscreen && (
                <div className="absolute top-2 left-2 z-10 flex items-center gap-2">
                  <button
                    onClick={() => setGraphFullscreen(false)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-white/10 hover:bg-white/20 text-white/70 hover:text-white text-xs transition-colors"
                  >
                    <Minimize2 className="w-3.5 h-3.5" /> Quitter plein ecran
                  </button>
                  <span className="text-[10px] text-white/30">
                    {graph ? `${graph.nodes.length} noeuds, ${graph.links.length} liens${graph.total_relations_unfiltered && graph.total_relations_unfiltered > graph.links.length ? ` / ${graph.total_relations_unfiltered} total` : ''}` : ''}
                  </span>
                </div>
              )}
              <RelationGraphEnhanced
                data={graph}
                isLoading={relLoading}
                onNodeClick={(node: GraphNode) => {
                  setSelectedNode(node);
                  if (!analytics) fetchAnalytics();
                }}
                enabledTypes={enabledTypes}
                enabledLevels={enabledLevels}
                searchQuery={graphSearch}
                selectedCommunity={selectedCommunity}
                colorMode={colorMode}
                analytics={analytics}
                fullscreen={graphFullscreen}
                onToggleFullscreen={() => setGraphFullscreen((prev) => !prev)}
              />
              {selectedNode && graph && (
                <NodeDetailPanel
                  node={selectedNode}
                  graphData={graph}
                  analytics={analytics}
                  onClose={() => setSelectedNode(null)}
                />
              )}
            </div>

            {/* What-If panel (conditional) */}
            {showWhatIf && graph && graph.nodes.length > 0 && (
              <WhatIfPanel
                nodes={graph.nodes}
                whatIfResult={whatIfResult}
                simulating={simulating}
                onSimulate={(actorId, depth) => whatif(actorId, depth)}
                onExport={async (format) => {
                  const data = await exportGraph(format);
                  if (data) {
                    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `relations-${relationsDept}.${format}`;
                    a.click();
                    URL.revokeObjectURL(url);
                  }
                }}
              />
            )}

            {/* Ecosystem score panel (conditional) */}
            {showEcosystem && (
              <EcosystemScorePanel data={ecosystemScore} isLoading={relLoading} />
            )}

            {/* Analytics panel (conditional) */}
            {showAnalytics && (
              <NetworkAnalyticsPanel analytics={analytics} isLoading={relLoading} />
            )}

            {/* Gaps panel (conditional) */}
            {showGaps && <GapsPanel gaps={gaps} isLoading={relLoading} />}
          </div>
        )}

        {/* No results after search */}
        {!loading && query.length >= 2 && results.length === 0 && activeTab === 'search' && !deptOverview && (
          <GlassCard>
            <GlassCardContent className="flex flex-col items-center justify-center py-12 text-center">
              <Search className="w-10 h-10 text-muted-foreground/30 mb-3" />
              <h3 className="text-base font-medium mb-1">Aucun resultat pour &quot;{query}&quot;</h3>
              <p className="text-sm text-muted-foreground">
                Essayez un SIREN (9 chiffres), un code departement, ou un mot-cle.
              </p>
            </GlassCardContent>
          </GlassCard>
        )}

        {/* Empty state */}
        {!loading && !query && results.length === 0 && !entity && !deptOverview && activeTab !== 'relations' && (
          <GlassCard>
            <GlassCardContent className="flex flex-col items-center justify-center py-16 text-center">
              <Shield className="w-12 h-12 text-muted-foreground/30 mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">Investigation Territoriale</h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Recherchez par SIREN, nom d&#39;entreprise, departement ou mot-cle pour explorer les signaux.
                Selectionnez un departement pour une vue d&#39;ensemble avec analyse LLM.
              </p>
            </GlassCardContent>
          </GlassCard>
        )}
      </div>
    </DashboardLayout>
  );
}
