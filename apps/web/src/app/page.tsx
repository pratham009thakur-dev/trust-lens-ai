"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Shield, ShieldAlert, ShieldCheck, Terminal, Activity, ArrowRight, BrainCircuit, Database } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function TrustLensDashboard() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  
  // NEW: State to hold our MongoDB history
  const [history, setHistory] = useState<any[]>([]);

  // NEW: Fetch history when the page loads
  const fetchHistory = async () => {
    try {
      const response = await axios.get("https://pratham9thakur-trustlens-ai.hf.space/api/v1/history");
      setHistory(response.data.history);
    } catch (err) {
      console.error("Could not fetch database history", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post("https://pratham9thakur-trustlens-ai.hf.space/api/v1/scan", { url });
      setResult(response.data);
      // Automatically refresh the history table after a new scan!
      fetchHistory();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to connect to the TrustLens AI Core.");
    } finally {
      setLoading(false);
    }
  };

  const getVerdictColor = (score: number) => {
    if (score >= 50) return "text-red-500 border-red-500/50 bg-red-500/10";
    return "text-emerald-400 border-emerald-400/50 bg-emerald-400/10";
  };

  const shapData = result?.explainability?.shap_breakdown
    ? Object.entries(result.explainability.shap_breakdown).map(([name, data]: [string, any]) => ({
        feature: name.replace("qty_", "").replace("_", " ").toUpperCase(),
        impact: data.impact_value,
      }))
    : [];

  return (
    <div className="min-h-screen bg-[#0B0F19] text-slate-200 font-sans p-6 md:p-12">
      <header className="flex items-center gap-3 mb-12 border-b border-slate-800 pb-6">
        <Shield className="w-8 h-8 text-emerald-500" />
        <h1 className="text-3xl font-bold tracking-wider text-white">
          TRUSTLENS <span className="text-emerald-500">AI</span>
        </h1>
        <div className="ml-auto flex items-center gap-2 text-xs font-mono text-slate-500">
          <Activity className="w-4 h-4 text-emerald-500 animate-pulse" />
          SYSTEM ONLINE
        </div>
      </header>

      <main className="max-w-5xl mx-auto space-y-8">
        {/* Scanner Component */}
        <div className="bg-[#161F30] border border-slate-700 rounded-xl p-8 shadow-2xl">
          <h2 className="text-xl font-semibold text-white mb-2 flex items-center gap-2">
            <Terminal className="w-5 h-5 text-emerald-400" />
            Threat Detection Matrix
          </h2>
          <p className="text-slate-400 text-sm mb-6">
            Enter a target URL below. The engine will extract structural telemetry and run XGBoost inference.
          </p>

          <form onSubmit={handleScan} className="flex flex-col md:flex-row gap-4">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://suspicious-link.com/login..."
              className="flex-1 bg-[#0B0F19] border border-slate-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all font-mono text-sm"
            />
            <button
              type="submit"
              disabled={loading || !url}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-8 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "ANALYZING..." : "INITIATE SCAN"}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm flex items-center gap-2">
              <ShieldAlert className="w-5 h-5" />
              {error}
            </div>
          )}
        </div>

        {/* Live Scan Results */}
        {result && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className={`col-span-1 md:col-span-2 rounded-xl p-6 border flex flex-col md:flex-row items-center gap-6 ${getVerdictColor(result.overall_risk_score)}`}>
              <div className="p-4 bg-[#0B0F19] rounded-full">
                {result.overall_risk_score >= 50 ? <ShieldAlert className="w-12 h-12 text-red-500" /> : <ShieldCheck className="w-12 h-12 text-emerald-400" />}
              </div>
              <div className="flex-1 text-center md:text-left">
                <p className="text-sm font-mono uppercase tracking-widest opacity-80 mb-1">AI Verdict</p>
                <h3 className="text-3xl font-bold mb-2">{result.verdict}</h3>
                <p className="opacity-90">{result.explanation}</p>
              </div>
              <div className="text-center bg-[#0B0F19] px-8 py-4 rounded-lg border border-current/20">
                <p className="text-xs font-mono uppercase opacity-70 mb-1">Risk Score</p>
                <p className="text-4xl font-bold">{result.overall_risk_score}<span className="text-lg opacity-50">/100</span></p>
              </div>
            </div>

            <div className="col-span-1 bg-[#161F30] border border-slate-700 rounded-xl p-6">
              <h4 className="text-sm font-mono text-slate-400 uppercase tracking-wider mb-6 flex items-center gap-2 border-b border-slate-700 pb-2">
                <BrainCircuit className="w-4 h-4 text-purple-400" />
                AI Explainability (SHAP Analysis)
              </h4>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={shapData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <XAxis type="number" hide />
                    <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip cursor={{ fill: '#334155', opacity: 0.4 }} contentStyle={{ backgroundColor: '#0B0F19', border: '1px solid #334155', color: '#fff' }} />
                    <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                      {shapData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.impact > 0 ? '#ef4444' : '#10b981'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="text-xs text-slate-500 text-center mt-4"><span className="text-red-400">Red</span> increases threat. <span className="text-emerald-400">Green</span> decreases threat.</p>
            </div>

            <div className="col-span-1 bg-[#161F30] border border-slate-700 rounded-xl p-6">
              <h4 className="text-sm font-mono text-slate-400 uppercase tracking-wider mb-6 border-b border-slate-700 pb-2">Raw Telemetry</h4>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { label: "Domain Entropy", value: result.metrics.domain_entropy },
                  { label: "URL Length", value: result.metrics.url_length },
                  { label: "Hyphens", value: result.metrics.qty_hyphens },
                  { label: "Scam Keywords", value: result.metrics.contains_scam_keywords },
                ].map((metric, idx) => (
                  <div key={idx} className="bg-[#0B0F19] p-4 rounded-lg border border-slate-800 flex flex-col justify-center">
                    <p className="text-xs font-mono text-slate-500 mb-1">{metric.label}</p>
                    <p className="text-xl font-semibold text-slate-200">{metric.value}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* NEW: MongoDB History Ledger */}
        <div className="bg-[#161F30] border border-slate-700 rounded-xl p-8 shadow-xl mt-8">
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-400" />
            Global Threat Ledger (MongoDB)
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-700 text-xs font-mono text-slate-500 uppercase tracking-wider">
                  <th className="p-3">Timestamp</th>
                  <th className="p-3">Target URL</th>
                  <th className="p-3">Score</th>
                  <th className="p-3">Verdict</th>
                </tr>
              </thead>
              <tbody>
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="p-6 text-center text-slate-500 font-mono text-sm">No scans logged in database yet.</td>
                  </tr>
                ) : (
                  history.map((scan, idx) => (
                    <tr key={idx} className="border-b border-slate-800 hover:bg-[#0B0F19] transition-colors">
                      <td className="p-3 text-xs text-slate-400 font-mono">
                        {new Date(scan.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </td>
                      <td className="p-3 text-sm text-slate-300 truncate max-w-[200px]" title={scan.target_url}>
                        {scan.target_url}
                      </td>
                      <td className="p-3">
                        <span className={`text-xs font-bold px-2 py-1 rounded ${scan.overall_risk_score >= 50 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                          {scan.overall_risk_score}
                        </span>
                      </td>
                      <td className="p-3 text-sm text-slate-300">{scan.verdict}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}