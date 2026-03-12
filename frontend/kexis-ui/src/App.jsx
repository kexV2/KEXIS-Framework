import { useState } from "react";

export default function App() {
  const [githubUsername, setGithubUsername] = useState("kexgh");
  const [mastodonHandle, setMastodonHandle] = useState("xgh@mastodon.social");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  async function runAnalysis() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          github_username: githubUsername,
          mastodon_handle: mastodonHandle,
        }),
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (err) {
      setError("Could not connect to the KEXIS backend.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  function resetInputs() {
    setGithubUsername("");
    setMastodonHandle("");
    setError("");
    setResult(null);
  }

  const confidenceScore = result?.result?.confidence_score ?? 0;
  const classification = result?.result?.classification ?? "No result yet";

  const usernameSimilarity = result?.features?.username_similarity ?? 0;
  const topicSimilarity = result?.features?.topic_similarity ?? 0;
  const activitySimilarity = result?.features?.activity_similarity ?? 0;
  const sharedKeywords = result?.features?.shared_keywords ?? [];

  const github = result?.github ?? {};
  const mastodon = result?.mastodon ?? {};

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-10">
          <div className="inline-flex items-center rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 text-xs font-medium text-cyan-200">
            KEXIS Framework
          </div>

          <h1 className="mt-4 text-4xl font-bold tracking-tight md:text-5xl">
            Cross-Platform OSINT Attribution
          </h1>

          <p className="mt-4 max-w-3xl text-base text-zinc-400 md:text-lg">
            Compare identity signals across GitHub and Mastodon using a
            structured confidence score and explainable evidence indicators.
          </p>
        </header>

        <div className="grid gap-8 lg:grid-cols-[420px_minmax(0,1fr)]">
          <section className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 shadow-2xl shadow-black/20 backdrop-blur">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">Run Analysis</h2>
                <p className="mt-1 text-sm text-zinc-400">
                  Enter platform identifiers and launch the attribution check.
                </p>
              </div>

              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  loading
                    ? "border border-amber-500/20 bg-amber-500/10 text-amber-200"
                    : "border border-emerald-500/20 bg-emerald-500/10 text-emerald-200"
                }`}
              >
                {loading ? "Running..." : "Ready"}
              </span>
            </div>

            <div className="mt-6 space-y-4">
              <Field
                label="GitHub Username"
                value={githubUsername}
                onChange={setGithubUsername}
                placeholder="e.g. octocat"
              />

              <Field
                label="Mastodon Handle"
                value={mastodonHandle}
                onChange={setMastodonHandle}
                placeholder="e.g. user@mastodon.social"
              />
            </div>

            <div className="mt-6 flex flex-wrap gap-3">
              <button
                onClick={runAnalysis}
                disabled={loading || !githubUsername || !mastodonHandle}
                className="rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-black transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "Running..." : "Run Attribution Analysis"}
              </button>

              <button
                onClick={resetInputs}
                className="rounded-2xl border border-white/10 bg-zinc-800 px-5 py-3 text-sm font-medium text-zinc-200 transition hover:bg-zinc-700"
              >
                Reset Inputs
              </button>
            </div>

            {error && (
              <div className="mt-5 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                {error}
              </div>
            )}
          </section>

          <section className="space-y-6">
            <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 shadow-2xl shadow-black/20 backdrop-blur">
              <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.2em] text-zinc-500">
                    Attribution Confidence
                  </p>
                  <h2 className="mt-2 text-5xl font-bold">
                    {confidenceScore.toFixed(2)}
                  </h2>
                  <p className="mt-2 text-lg text-zinc-300">{classification}</p>
                </div>

                <div className="rounded-2xl border border-violet-500/20 bg-violet-500/10 px-4 py-3 text-sm text-violet-200">
                  Confidence score {Math.round(confidenceScore * 100)}%
                </div>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-3">
                <MetricCard
                  title="Username Similarity"
                  value={usernameSimilarity.toFixed(2)}
                  tone="cyan"
                />
                <MetricCard
                  title="Topic Similarity"
                  value={topicSimilarity.toFixed(2)}
                  tone="violet"
                />
                <MetricCard
                  title="Activity Similarity"
                  value={activitySimilarity.toFixed(2)}
                  tone="cyan"
                />
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <EvidenceCard
                title="GitHub Evidence"
                accent="cyan"
                rows={[
                  ["Username", github.username ?? "—"],
                  ["Bio", github.bio ?? "—"],
                  ["Public Repos", github.public_repos ?? "—"],
                  ["Followers", github.followers ?? "—"],
                  ["Following", github.following ?? "—"],
                ]}
                chips={github.languages ?? []}
                chipLabel="Languages"
                footerItems={github.repo_names ?? []}
                footerLabel="Repository Names"
              />

              <EvidenceCard
                title="Mastodon Evidence"
                accent="violet"
                rows={[
                  ["Username", mastodon.username ?? "—"],
                  ["Handle", mastodon.handle ?? "—"],
                  ["Display Name", mastodon.display_name ?? "—"],
                  ["Bio", mastodon.bio ?? "—"],
                  ["Followers", mastodon.followers ?? "—"],
                  ["Following", mastodon.following ?? "—"],
                ]}
                chips={mastodon.posts ?? []}
                chipLabel="Recent Posts"
                footerItems={mastodon.profile_url ? [mastodon.profile_url] : []}
                footerLabel="Profile URL"
              />
            </div>

            <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 shadow-2xl shadow-black/20 backdrop-blur">
              <h3 className="text-xl font-semibold">Shared Indicators</h3>
              <p className="mt-2 text-sm text-zinc-400">
                Evidence overlap currently detected across the two sources.
              </p>

              <div className="mt-5">
                <p className="mb-3 text-sm font-medium text-zinc-300">
                  Shared Keywords
                </p>

                <div className="flex flex-wrap gap-2">
                  {sharedKeywords.length ? (
                    sharedKeywords.map((word) => (
                      <span
                        key={word}
                        className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200"
                      >
                        {word}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-zinc-500">None detected</span>
                  )}
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 shadow-2xl shadow-black/20 backdrop-blur">
              <h3 className="text-xl font-semibold">Behavioural Activity Evidence</h3>
              <p className="mt-2 text-sm text-zinc-400">
                This section will populate once your backend returns activity
                similarity data and activity timing summaries.
              </p>

              <div className="mt-6 grid gap-6 md:grid-cols-2">
                <div className="rounded-2xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                  <p className="text-sm font-medium text-cyan-300">
                    GitHub Top Active Hours
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(github.top_active_hours ?? []).length ? (
                      github.top_active_hours.map((hour) => (
                        <span
                          key={`gh-${hour}`}
                          className="rounded-full border border-cyan-500/20 bg-cyan-500/10 px-3 py-1 text-xs text-cyan-200"
                        >
                          {hour}:00
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-zinc-500">
                        No activity data yet
                      </span>
                    )}
                  </div>

                  <p className="mt-4 text-xs text-zinc-500">
                    Sample size: {github.activity_sample_size ?? 0}
                  </p>
                </div>

                <div className="rounded-2xl border border-violet-500/20 bg-violet-500/5 p-4">
                  <p className="text-sm font-medium text-violet-300">
                    Mastodon Top Active Hours
                  </p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(mastodon.top_active_hours ?? []).length ? (
                      mastodon.top_active_hours.map((hour) => (
                        <span
                          key={`md-${hour}`}
                          className="rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1 text-xs text-violet-200"
                        >
                          {hour}:00
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-zinc-500">
                        No activity data yet
                      </span>
                    )}
                  </div>

                  <p className="mt-4 text-xs text-zinc-500">
                    Sample size: {mastodon.activity_sample_size ?? 0}
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-zinc-300">
        {label}
      </span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-2xl border border-white/10 bg-zinc-950 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-500 focus:border-cyan-400/50"
      />
    </label>
  );
}

function MetricCard({ title, value, tone = "cyan" }) {
  const toneClasses = {
    cyan: "border-cyan-500/20 bg-cyan-500/10 text-cyan-200",
    violet: "border-violet-500/20 bg-violet-500/10 text-violet-200",
  };

  return (
    <div
      className={`rounded-2xl border p-4 ${toneClasses[tone] ?? toneClasses.cyan}`}
    >
      <p className="text-sm font-medium">{title}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

function EvidenceCard({
  title,
  rows = [],
  chips = [],
  chipLabel,
  footerItems = [],
  footerLabel,
  accent = "cyan",
}) {
  const accentBar = accent === "violet" ? "bg-violet-400" : "bg-cyan-400";

  return (
    <div className="rounded-3xl border border-white/10 bg-zinc-900/70 p-6 shadow-2xl shadow-black/20 backdrop-blur">
      <div className="mb-5 flex items-center gap-3">
        <div className={`h-8 w-1 rounded-full ${accentBar}`} />
        <h3 className="text-xl font-semibold">{title}</h3>
      </div>

      <div className="space-y-3">
        {rows.length ? (
          rows.map(([label, value]) => (
            <div
              key={`${title}-${label}`}
              className="flex items-start justify-between gap-4 rounded-2xl border border-white/5 bg-zinc-950/60 px-4 py-3"
            >
              <span className="text-sm text-zinc-400">{label}</span>
              <span className="max-w-[60%] text-right text-sm text-zinc-200">
                {String(value)}
              </span>
            </div>
          ))
        ) : (
          <p className="text-sm text-zinc-500">No results yet</p>
        )}
      </div>

      <div className="mt-5">
        <p className="mb-3 text-sm font-medium text-zinc-300">{chipLabel}</p>
        <div className="flex flex-wrap gap-2">
          {chips.length ? (
            chips.map((chip, index) => (
              <span
                key={`${title}-chip-${index}`}
                className="rounded-full border border-white/10 bg-zinc-800 px-3 py-1 text-xs text-zinc-200"
              >
                {chip}
              </span>
            ))
          ) : (
            <span className="text-sm text-zinc-500">None detected</span>
          )}
        </div>
      </div>

      <div className="mt-5">
        <p className="mb-3 text-sm font-medium text-zinc-300">{footerLabel}</p>
        <div className="space-y-2">
          {footerItems.length ? (
            footerItems.map((item, index) => (
              <div
                key={`${title}-footer-${index}`}
                className="rounded-2xl border border-white/5 bg-zinc-950/60 px-4 py-3 text-sm text-zinc-300"
              >
                {item}
              </div>
            ))
          ) : (
            <span className="text-sm text-zinc-500">None detected</span>
          )}
        </div>
      </div>
    </div>
  );
}