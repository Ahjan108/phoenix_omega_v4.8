import { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  AreaChart, Area, PieChart, Pie, Cell, ResponsiveContainer,
  LineChart, Line, ComposedChart
} from "recharts";

const COLORS = {
  bg: "#0B0F1A",
  card: "#131825",
  cardBorder: "#1E2536",
  accent: "#6366F1",
  accentLight: "#818CF8",
  green: "#34D399",
  greenDark: "#059669",
  amber: "#FBBF24",
  red: "#F87171",
  coral: "#FB7185",
  sky: "#38BDF8",
  text: "#E2E8F0",
  textMuted: "#94A3B8",
  textDim: "#64748B",
};

const CHART_COLORS = ["#6366F1", "#34D399", "#FBBF24", "#FB7185", "#38BDF8", "#A78BFA"];

const monthlyRamp = [
  { month: "M1", gp: 1800, fv: 400, total: 2200, label: "Jan" },
  { month: "M2", gp: 2800, fv: 800, total: 3600, label: "Feb" },
  { month: "M3", gp: 3600, fv: 1400, total: 5000, label: "Mar" },
  { month: "M4", gp: 4200, fv: 2000, total: 6200, label: "Apr" },
  { month: "M5", gp: 4800, fv: 2400, total: 7200, label: "May" },
  { month: "M6", gp: 5200, fv: 2800, total: 8000, label: "Jun" },
  { month: "M7", gp: 5400, fv: 3000, total: 8400, label: "Jul" },
  { month: "M8", gp: 5600, fv: 3200, total: 8800, label: "Aug" },
  { month: "M9", gp: 5800, fv: 3400, total: 9200, label: "Sep" },
  { month: "M10", gp: 6000, fv: 3500, total: 9500, label: "Oct" },
  { month: "M11", gp: 6200, fv: 3600, total: 9800, label: "Nov" },
  { month: "M12", gp: 6400, fv: 3800, total: 10200, label: "Dec" },
];

const cumulativeData = monthlyRamp.reduce((acc, item, i) => {
  const prev = i > 0 ? acc[i - 1] : { cumGP: 0, cumFV: 0, cumTotal: 0 };
  acc.push({
    ...item,
    cumGP: prev.cumGP + item.gp,
    cumFV: prev.cumFV + item.fv,
    cumTotal: prev.cumTotal + item.total,
  });
  return acc;
}, []);

const scenarioData = [
  { scenario: "Downside", gp: 21000, fv: 8000, total: 29000 },
  { scenario: "Conservative", gp: 36000, fv: 14000, total: 50000 },
  { scenario: "Most Likely", gp: 48000, fv: 20000, total: 68000 },
  { scenario: "Optimistic", gp: 72000, fv: 36000, total: 108000 },
  { scenario: "Upside", gp: 96000, fv: 48000, total: 144000 },
];

const clusterData = [
  { cluster: "Nervous System", brands: 9, books: 378, gpRev: 2700, fvRev: 1800, totalRev: 4500, pctTotal: 42 },
  { cluster: "Productivity", brands: 6, books: 252, gpRev: 1560, fvRev: 1020, totalRev: 2580, pctTotal: 24 },
  { cluster: "Vitality", brands: 3, books: 126, gpRev: 660, fvRev: 420, totalRev: 1080, pctTotal: 10 },
  { cluster: "Relationships", brands: 3, books: 126, gpRev: 600, fvRev: 390, totalRev: 990, pctTotal: 9 },
  { cluster: "Identity", brands: 2, books: 84, gpRev: 380, fvRev: 240, totalRev: 620, pctTotal: 6 },
  { cluster: "Gen Z", brands: 1, books: 42, gpRev: 240, fvRev: 180, totalRev: 420, pctTotal: 4 },
  { cluster: "Wisdom", brands: 1, books: 42, gpRev: 260, fvRev: 170, totalRev: 430, pctTotal: 4 },
];

const platformSplit = [
  { name: "Google Play Books", value: 62, color: "#6366F1" },
  { name: "INaudio / Findaway", value: 38, color: "#34D399" },
];

const fvBreakdown = [
  { name: "Apple Books", value: 22, color: "#38BDF8" },
  { name: "Spotify", value: 20, color: "#34D399" },
  { name: "Libraries", value: 18, color: "#A78BFA" },
  { name: "Kobo", value: 15, color: "#FBBF24" },
  { name: "Chirp/Other", value: 25, color: "#FB7185" },
];

const topBrands = [
  { brand: "stabilizer", cluster: "Nervous System", monthlyRev: 520, cr: 2.8, completion: 68 },
  { brand: "panic_first_aid", cluster: "Nervous System", monthlyRev: 480, cr: 3.1, completion: 72 },
  { brand: "adhd_anchor", cluster: "Productivity", monthlyRev: 440, cr: 2.6, completion: 61 },
  { brand: "sleep_repair", cluster: "Nervous System", monthlyRev: 410, cr: 2.4, completion: 74 },
  { brand: "breathwork_lab", cluster: "Nervous System", monthlyRev: 390, cr: 2.5, completion: 70 },
  { brand: "dopamine_balance", cluster: "Productivity", monthlyRev: 360, cr: 2.3, completion: 58 },
  { brand: "focus_forge", cluster: "Productivity", monthlyRev: 340, cr: 2.2, completion: 55 },
  { brand: "somatic_reset", cluster: "Nervous System", monthlyRev: 320, cr: 2.1, completion: 65 },
];

const y2Projection = [
  { month: "Y1 Q1", y1: 10800, y2: null },
  { month: "Y1 Q2", y1: 21400, y2: null },
  { month: "Y1 Q3", y1: 26400, y2: null },
  { month: "Y1 Q4", y1: 29500, y2: null },
  { month: "Y2 Q1", y1: null, y2: 38000 },
  { month: "Y2 Q2", y1: null, y2: 52000 },
  { month: "Y2 Q3", y1: null, y2: 68000 },
  { month: "Y2 Q4", y1: null, y2: 82000 },
];

function Card({ children, className = "" }) {
  return (
    <div style={{
      background: COLORS.card,
      border: `1px solid ${COLORS.cardBorder}`,
      borderRadius: 12,
      padding: "20px 24px",
      ...( className === "span2" ? { gridColumn: "span 2" } : {}),
      ...( className === "span3" ? { gridColumn: "span 3" } : {}),
    }}>
      {children}
    </div>
  );
}

function StatCard({ label, value, sub, accent = false }) {
  return (
    <div style={{
      background: accent ? "linear-gradient(135deg, #1E1B4B, #312E81)" : COLORS.card,
      border: `1px solid ${accent ? "#4338CA" : COLORS.cardBorder}`,
      borderRadius: 12,
      padding: "20px 24px",
    }}>
      <div style={{ fontSize: 12, color: COLORS.textMuted, textTransform: "uppercase", letterSpacing: 1.2, marginBottom: 6, fontFamily: "'JetBrains Mono', monospace" }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: accent ? "#A5B4FC" : COLORS.text, fontFamily: "'JetBrains Mono', monospace" }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: COLORS.textDim, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function SectionTitle({ children, sub }) {
  return (
    <div style={{ marginBottom: 8, marginTop: 32 }}>
      <h2 style={{ fontSize: 18, fontWeight: 700, color: COLORS.text, margin: 0, fontFamily: "'Space Grotesk', sans-serif" }}>{children}</h2>
      {sub && <p style={{ fontSize: 13, color: COLORS.textDim, margin: "4px 0 0" }}>{sub}</p>}
    </div>
  );
}

function CustomTooltip({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#1E2536",
      border: "1px solid #334155",
      borderRadius: 8,
      padding: "10px 14px",
      fontSize: 12,
      color: COLORS.text,
    }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2 }}>
          <div style={{ width: 8, height: 8, borderRadius: 2, background: p.color }} />
          <span style={{ color: COLORS.textMuted }}>{p.name}:</span>
          <span style={{ fontWeight: 600, fontFamily: "'JetBrains Mono', monospace" }}>
            {formatter ? formatter(p.value) : `$${p.value.toLocaleString()}`}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function RevenueDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "monthly", label: "Monthly Ramp" },
    { id: "brands", label: "Brand Performance" },
    { id: "platforms", label: "Platform Split" },
  ];

  return (
    <div style={{
      background: COLORS.bg,
      color: COLORS.text,
      minHeight: "100vh",
      fontFamily: "'Inter', -apple-system, sans-serif",
      padding: "32px 28px",
    }}>
      <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
          <div style={{ width: 10, height: 10, borderRadius: "50%", background: COLORS.green }} />
          <span style={{ fontSize: 11, color: COLORS.green, textTransform: "uppercase", letterSpacing: 1.5, fontWeight: 600 }}>Confidential • SpiritualTech Systems</span>
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 700, margin: 0, fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1.2 }}>
          Revenue Projection Report
        </h1>
        <p style={{ color: COLORS.textMuted, fontSize: 14, margin: "6px 0 0" }}>
          Canonical Multi-Brand Plan v1.2 — 1,008 Books × 24 Brands × 2 Platforms — Organic Only
        </p>
        <p style={{ color: COLORS.textDim, fontSize: 12, margin: "2px 0 0" }}>
          Prepared February 2026 • No paid advertising, social media, or external promotion assumed
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 28, borderBottom: `1px solid ${COLORS.cardBorder}`, paddingBottom: 0 }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              background: activeTab === tab.id ? COLORS.card : "transparent",
              color: activeTab === tab.id ? COLORS.text : COLORS.textDim,
              border: activeTab === tab.id ? `1px solid ${COLORS.cardBorder}` : "1px solid transparent",
              borderBottom: activeTab === tab.id ? `1px solid ${COLORS.card}` : "1px solid transparent",
              borderRadius: "8px 8px 0 0",
              padding: "10px 20px",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
              marginBottom: -1,
              transition: "all 0.2s",
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW TAB */}
      {activeTab === "overview" && (
        <div>
          {/* KPI Row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12, marginBottom: 24 }}>
            <StatCard label="Total Books" value="1,008" sub="42 per brand × 24 brands" />
            <StatCard label="Y1 Most Likely" value="$68K" sub="$50K–$78K range" accent />
            <StatCard label="Steady-State" value="$5.5K/mo" sub="By Month 8–10" />
            <StatCard label="Avg Per Brand" value="$236/mo" sub="$113–$415 range" />
            <StatCard label="Break-Even" value="Month 3" sub="$0 fixed costs" />
          </div>

          {/* Scenario Chart */}
          <SectionTitle sub="Year 1 total revenue across Google Play Books + INaudio (Findaway Voices) distribution">Revenue Scenarios — Year 1</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={scenarioData} barGap={8}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" />
                <XAxis dataKey="scenario" tick={{ fill: COLORS.textMuted, fontSize: 12 }} />
                <YAxis tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12, color: COLORS.textMuted }} />
                <Bar dataKey="gp" name="Google Play" fill={COLORS.accent} radius={[4, 4, 0, 0]} />
                <Bar dataKey="fv" name="INaudio / FV" fill={COLORS.green} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", justifyContent: "center", gap: 32, marginTop: 12, fontSize: 12 }}>
              <span style={{ color: COLORS.textDim }}>▼ Downside: <span style={{ color: COLORS.red, fontWeight: 600 }}>$29K</span></span>
              <span style={{ color: COLORS.textDim }}>● Most Likely: <span style={{ color: COLORS.accentLight, fontWeight: 700 }}>$68K</span></span>
              <span style={{ color: COLORS.textDim }}>▲ Upside: <span style={{ color: COLORS.green, fontWeight: 600 }}>$144K</span></span>
            </div>
          </Card>

          {/* Cluster Revenue */}
          <SectionTitle sub="Monthly steady-state revenue by brand cluster (most likely scenario)">Revenue by Cluster</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={clusterData} layout="vertical" barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" horizontal={false} />
                <XAxis type="number" tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${v.toLocaleString()}`} />
                <YAxis type="category" dataKey="cluster" tick={{ fill: COLORS.textMuted, fontSize: 12 }} width={100} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="gpRev" name="Google Play" fill={COLORS.accent} stackId="a" radius={[0, 0, 0, 0]} />
                <Bar dataKey="fvRev" name="INaudio" fill={COLORS.green} stackId="a" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Key Assumptions */}
          <SectionTitle>Key Assumptions</SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            <Card>
              <div style={{ fontSize: 11, color: COLORS.accent, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10, fontWeight: 600 }}>Pricing</div>
              <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
                <div>Blended ASP: <span style={{ color: COLORS.text, fontWeight: 600 }}>$6.00–$6.50</span></div>
                <div>Micro-sessions: <span style={{ color: COLORS.text }}>$1.99–$7.99</span></div>
                <div>Deep dives: <span style={{ color: COLORS.text }}>$14.99–$29.99</span></div>
                <div>Series bundle discount: <span style={{ color: COLORS.text }}>15–25%</span></div>
              </div>
            </Card>
            <Card>
              <div style={{ fontSize: 11, color: COLORS.green, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10, fontWeight: 600 }}>Conversion</div>
              <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
                <div>Blended CR: <span style={{ color: COLORS.text, fontWeight: 600 }}>1.5–2.5%</span></div>
                <div>High-intent (panic, ADHD): <span style={{ color: COLORS.text }}>2.5–3.5%</span></div>
                <div>Browse-intent (wisdom): <span style={{ color: COLORS.text }}>0.8–1.5%</span></div>
                <div>Impressions/book: <span style={{ color: COLORS.text }}>200–800/mo</span></div>
              </div>
            </Card>
            <Card>
              <div style={{ fontSize: 11, color: COLORS.amber, textTransform: "uppercase", letterSpacing: 1, marginBottom: 10, fontWeight: 600 }}>Platform Splits</div>
              <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
                <div>Google Play: <span style={{ color: COLORS.text, fontWeight: 600 }}>70% publisher split</span></div>
                <div>INaudio: <span style={{ color: COLORS.text }}>80% of net revenue</span></div>
                <div>Library streams: <span style={{ color: COLORS.text }}>$1.50–$4.00/checkout</span></div>
                <div>Spotify pool: <span style={{ color: COLORS.text }}>$0.005–$0.02/min</span></div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* MONTHLY RAMP TAB */}
      {activeTab === "monthly" && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
            <StatCard label="Month 1" value="$2.2K" sub="Indexing + discovery" />
            <StatCard label="Month 6" value="$8.0K" sub="Reviews → recommendations" accent />
            <StatCard label="Month 12" value="$10.2K" sub="Series authority + repeat" />
            <StatCard label="Y1 Cumulative" value="$88K" sub="Most likely total" />
          </div>

          <SectionTitle sub="Monthly revenue ramp from launch through Month 12 (most likely scenario)">Monthly Revenue Ramp</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={360}>
              <AreaChart data={monthlyRamp}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" />
                <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                <YAxis tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${(v/1000).toFixed(1)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Area type="monotone" dataKey="gp" name="Google Play" stroke={COLORS.accent} fill={COLORS.accent} fillOpacity={0.3} strokeWidth={2} />
                <Area type="monotone" dataKey="fv" name="INaudio" stroke={COLORS.green} fill={COLORS.green} fillOpacity={0.2} strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          <SectionTitle sub="Running total across Year 1">Cumulative Revenue</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={320}>
              <LineChart data={cumulativeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" />
                <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                <YAxis tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line type="monotone" dataKey="cumGP" name="Google Play (cum.)" stroke={COLORS.accent} strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="cumFV" name="INaudio (cum.)" stroke={COLORS.green} strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="cumTotal" name="Total" stroke={COLORS.amber} strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Y2 Projection */}
          <SectionTitle sub="Quarterly revenue including Year 2 scale-up projection (double-down on winners)">Year 1 → Year 2 Trajectory</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={y2Projection} barGap={2}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" />
                <XAxis dataKey="month" tick={{ fill: COLORS.textMuted, fontSize: 11 }} />
                <YAxis tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="y1" name="Year 1" fill={COLORS.accent} radius={[4, 4, 0, 0]} />
                <Bar dataKey="y2" name="Year 2 (projected)" fill={COLORS.green} radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <div style={{ textAlign: "center", fontSize: 12, color: COLORS.textDim, marginTop: 8 }}>
              Year 2 assumes kill bottom 30% of brands, double catalog for top 30%, add 500+ titles → projected $180K–$240K Y2
            </div>
          </Card>
        </div>
      )}

      {/* BRANDS TAB */}
      {activeTab === "brands" && (
        <div>
          <SectionTitle sub="Projected top 8 performing brands by monthly revenue at steady-state">Top Performing Brands</SectionTitle>
          <Card>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={topBrands} layout="vertical" barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2536" horizontal={false} />
                <XAxis type="number" tick={{ fill: COLORS.textMuted, fontSize: 11 }} tickFormatter={v => `$${v}`} />
                <YAxis type="category" dataKey="brand" tick={{ fill: COLORS.textMuted, fontSize: 11 }} width={120} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="monthlyRev" name="Monthly Revenue" fill={COLORS.accent} radius={[0, 6, 6, 0]}>
                  {topBrands.map((entry, i) => (
                    <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* Brand Performance Table */}
          <SectionTitle sub="Detailed metrics for projected top performers">Brand Metrics</SectionTitle>
          <Card>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: `1px solid ${COLORS.cardBorder}` }}>
                    {["Brand", "Cluster", "Monthly Rev", "Est. CR", "Completion", "Status"].map(h => (
                      <th key={h} style={{ padding: "10px 12px", textAlign: "left", color: COLORS.textDim, fontSize: 11, textTransform: "uppercase", letterSpacing: 1, fontWeight: 600 }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {topBrands.map((b, i) => (
                    <tr key={i} style={{ borderBottom: `1px solid ${COLORS.cardBorder}22` }}>
                      <td style={{ padding: "10px 12px", fontWeight: 600, fontFamily: "'JetBrains Mono', monospace", fontSize: 12 }}>{b.brand}</td>
                      <td style={{ padding: "10px 12px", color: COLORS.textMuted }}>{b.cluster}</td>
                      <td style={{ padding: "10px 12px", fontFamily: "'JetBrains Mono', monospace", fontWeight: 600, color: COLORS.green }}>${b.monthlyRev}</td>
                      <td style={{ padding: "10px 12px", fontFamily: "'JetBrains Mono', monospace" }}>{b.cr}%</td>
                      <td style={{ padding: "10px 12px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                          <div style={{ width: 60, height: 6, background: COLORS.cardBorder, borderRadius: 3 }}>
                            <div style={{ width: `${b.completion}%`, height: 6, background: b.completion > 65 ? COLORS.green : b.completion > 55 ? COLORS.amber : COLORS.red, borderRadius: 3 }} />
                          </div>
                          <span style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace" }}>{b.completion}%</span>
                        </div>
                      </td>
                      <td style={{ padding: "10px 12px" }}>
                        <span style={{
                          background: i < 3 ? "#064E3B" : "#1E3A5F",
                          color: i < 3 ? COLORS.green : COLORS.sky,
                          padding: "3px 10px",
                          borderRadius: 20,
                          fontSize: 11,
                          fontWeight: 600,
                        }}>
                          {i < 3 ? "DOUBLE DOWN" : "MONITOR"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Kill / Double-Down */}
          <SectionTitle sub="90-day decision matrix based on kill/double-down metrics">Portfolio Decision Framework</SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
            <Card>
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 36, fontWeight: 700, color: COLORS.green, fontFamily: "'JetBrains Mono', monospace" }}>5–6</div>
                <div style={{ fontSize: 11, color: COLORS.green, textTransform: "uppercase", letterSpacing: 1, fontWeight: 600 }}>Double Down</div>
              </div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6 }}>
                CR &gt;3%, Completion &gt;55%, Review velocity positive. Expand catalog to 80+ titles per brand.
              </div>
            </Card>
            <Card>
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 36, fontWeight: 700, color: COLORS.amber, fontFamily: "'JetBrains Mono', monospace" }}>10–12</div>
                <div style={{ fontSize: 11, color: COLORS.amber, textTransform: "uppercase", letterSpacing: 1, fontWeight: 600 }}>Monitor</div>
              </div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6 }}>
                CR 1.5–3%, mixed signals. Test title variations, pricing adjustments, cover art refresh.
              </div>
            </Card>
            <Card>
              <div style={{ textAlign: "center", marginBottom: 12 }}>
                <div style={{ fontSize: 36, fontWeight: 700, color: COLORS.red, fontFamily: "'JetBrains Mono', monospace" }}>6–8</div>
                <div style={{ fontSize: 11, color: COLORS.red, textTransform: "uppercase", letterSpacing: 1, fontWeight: 600 }}>Kill</div>
              </div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.6 }}>
                CR &lt;1.5%, Completion &lt;35%, zero reviews. Freeze catalog, reallocate resources to winners.
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* PLATFORMS TAB */}
      {activeTab === "platforms" && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
            <StatCard label="Google Play" value="62%" sub="Direct search → purchase" accent />
            <StatCard label="INaudio Total" value="38%" sub="Wide distribution network" />
            <StatCard label="GP Net Rate" value="70%" sub="Publisher revenue share" />
            <StatCard label="FV Net Rate" value="80%" sub="After retailer splits" />
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <SectionTitle sub="Revenue contribution by primary platform">Platform Revenue Split</SectionTitle>
              <Card>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={platformSplit}
                      cx="50%" cy="50%"
                      innerRadius={70} outerRadius={110}
                      dataKey="value"
                      stroke="none"
                    >
                      {platformSplit.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => `${v}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ display: "flex", justifyContent: "center", gap: 24, fontSize: 12 }}>
                  {platformSplit.map((p, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <div style={{ width: 10, height: 10, borderRadius: 2, background: p.color }} />
                      <span style={{ color: COLORS.textMuted }}>{p.name}: <span style={{ color: COLORS.text, fontWeight: 600 }}>{p.value}%</span></span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <div>
              <SectionTitle sub="Revenue distribution across INaudio retail partners">INaudio Distribution Breakdown</SectionTitle>
              <Card>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={fvBreakdown}
                      cx="50%" cy="50%"
                      innerRadius={70} outerRadius={110}
                      dataKey="value"
                      stroke="none"
                    >
                      {fvBreakdown.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => `${v}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: 16, fontSize: 11 }}>
                  {fvBreakdown.map((p, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 5 }}>
                      <div style={{ width: 8, height: 8, borderRadius: 2, background: p.color }} />
                      <span style={{ color: COLORS.textMuted }}>{p.name}: <span style={{ color: COLORS.text, fontWeight: 600 }}>{p.value}%</span></span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </div>

          {/* Platform Strategy */}
          <SectionTitle sub="How each platform contributes to the revenue engine">Platform Strategy Notes</SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
            <Card>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #4338CA, #6366F1)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700 }}>G</div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>Google Play Books</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim }}>Primary revenue + discovery engine</div>
                </div>
              </div>
              <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
                <div>• Direct search-to-purchase intent captures highest CR</div>
                <div>• Auto-narration pipeline = $0 production cost</div>
                <div>• Series bundles (15–35% discount tiers) drive LTV</div>
                <div>• Completion rates feed recommendation algorithm</div>
                <div>• Price must be ≤ all other platforms (compliance rule)</div>
              </div>
            </Card>
            <Card>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #059669, #34D399)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 700 }}>I</div>
                <div>
                  <div style={{ fontWeight: 600, fontSize: 14 }}>INaudio (Findaway Voices)</div>
                  <div style={{ fontSize: 11, color: COLORS.textDim }}>Wide distribution + passive baseline</div>
                </div>
              </div>
              <div style={{ fontSize: 13, color: COLORS.textMuted, lineHeight: 1.8 }}>
                <div>• 30+ retailers: Apple, Spotify, Kobo, libraries, Chirp</div>
                <div>• AI narration accepted (Google Play or ElevenLabs source)</div>
                <div>• Library checkouts provide steady baseline revenue</div>
                <div>• Slower ramp (2–4 weeks per title review + propagation)</div>
                <div>• 80/20 split — author keeps 80% of net royalties</div>
              </div>
            </Card>
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{
        marginTop: 48,
        paddingTop: 20,
        borderTop: `1px solid ${COLORS.cardBorder}`,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
      }}>
        <div style={{ fontSize: 11, color: COLORS.textDim }}>
          SpiritualTech Systems • Canonical Multi-Brand Plan v1.2 • Organic Revenue Projection
        </div>
        <div style={{ fontSize: 11, color: COLORS.textDim }}>
          All projections based on 2025–2026 indie self-help benchmarks • No paid promotion assumed
        </div>
      </div>
    </div>
  );
}
