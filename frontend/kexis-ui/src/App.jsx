import { useState } from "react";

export default function KexisUIMockup() {
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
  const sharedKeywords = result?.features?.shared_keywords ?? [];

  const github = result?.github;
  const mastodon = result?.mastodon;

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">
      <div className="mx-auto max-w-7xl px-6 py-10">
        <header className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="mb-3 inline-flex items-center rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-medium tracking-[0.25em] text-cyan-300 uppercase">
              KEXIS Framework
            </div>
            <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Cross-Platform OSINT Attribution
            </h1>
            <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base">
              Compare identity signals across GitHub and Mastodon using a structured confidence score.
            </p>
          </div>
        </header>

        <section className="mb-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/20">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-white">Run Analysis</h2>
                <p className="mt-1 text-sm text-zinc-400">
                  Enter platform identifiers and launch the attribution check.
                </p>
              </div>
              <div className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-300">
                {loading ? "Running..." : "Ready"}
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field
                label="GitHub Username"
                value={githubUsername}
                onChange={setGithubUsername}
                placeholder="e.g. kexgh"
              />
              <Field
                label="Mastodon Handle"
                value={mastodonHandle}
                onChange={setMastodonHandle}
                placeholder="e.g. xgh@mastodon.social"
              />
            </div>

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <button
                onClick={runAnalysis}
                disabled={loading}
                className="inline-flex items-center justify-center rounded-2xl bg-cyan-400 px-5 py-3 text-sm font-semibold text-zinc-950 transition hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Running..." : "Run Attribution Analysis"}
              </button>
              <button
                onClick={resetInputs}
                className="inline-flex items-center justify-center rounded-2xl border border-white/10 bg-zinc-900 px-5 py-3 text-sm font-medium text-zinc-200 transition hover:border-white/20 hover:bg-zinc-800"
              >
                Reset Inputs
              </button>
            </div>

            {error && (
              <div className="mt-4 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                {error}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-cyan-500/10 via-white/5 to-fuchsia-500/10 p-6 shadow-2xl shadow-black/20">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm text-zinc-400">Attribution Confidence</p>
                <h3 className="mt-2 text-5xl font-semibold tracking-tight text-white">
                  {confidenceScore.toFixed(2)}
                </h3>
                <p className="mt-2 text-sm text-zinc-300">{classification}</p>
              </div>
              <span className="rounded-full border border-amber-400/30 bg-amber-400/10 px-3 py-1 text-xs font-medium text-amber-300">
                {classification}
              </span>
            </div>

            <div className="mt-6">
              <div className="mb-2 flex items-center justify-between text-sm text-zinc-300">
                <span>Confidence score</span>
                <span>{Math.round(confidenceScore * 100)}%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-white/10">
                <div
                  className="h-full rounded-full bg-cyan-400"
                  style={{ width: `${Math.round(confidenceScore * 100)}%` }}
                />
              </div>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-3">
              <MetricCard title="Username Similarity" value={usernameSimilarity.toFixed(2)} tone="cyan" />
              <MetricCard title="Topic Similarity" value={topicSimilarity.toFixed(2)} tone="violet" />
            </div>
          </div>
        </section>

        <section className="mb-8 grid gap-6 xl:grid-cols-[1fr_1fr_0.8fr]">
          <EvidenceCard
            title="GitHub Evidence"
            accent="cyan"
            rows={
              github
                ? [
                    ["Username", github.username],
                    ["Bio", github.bio],
                    ["Repositories", String(github.public_repos)],
                    ["Followers", String(github.followers)],
                    ["Following", String(github.following)],
                  ]
                : []
            }
            chips={github?.languages ?? []}
            chipLabel="Languages"
            footerItems={github?.repo_names ?? []}
            footerLabel="Repository Names"
          />

          <EvidenceCard
            title="Mastodon Evidence"
            accent="violet"
            rows={
              mastodon
                ? [
                    ["Username", mastodon.username],
                    ["Handle", mastodon.handle],
                    ["Display Name", mastodon.display_name],
                    ["Bio", mastodon.bio],
                    ["Followers", String(mastodon.followers)],
                    ["Following", String(mastodon.following)],
                  ]
                : []
            }
            chips={mastodon?.posts ?? []}
            chipLabel="Recent Posts"
            footerItems={mastodon?.profile_url ? [mastodon.profile_url] : []}
            footerLabel="Profile URL"
          />

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/20">
            <h3 className="text-lg font-semibold text-white">Shared Indicators</h3>
            <p className="mt-1 text-sm text-zinc-400">
              Evidence overlap currently detected across the two sources.
            </p>

            <div className="mt-5 rounded-2xl border border-white/10 bg-zinc-900/70 p-4">
              <p className="text-xs uppercase tracking-[0.2em] text-zinc-500">
                Shared Keywords
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {sharedKeywords.length ? (
                  sharedKeywords.map((word) => (
                    <span
                      key={word}
                      className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-sm text-cyan-200"
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
        </section>
      </div>
    </div>
  );
}

function Field({ label, value, onChange, placeholder }) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-medium text-zinc-300">{label}</span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-2xl border border-white/10 bg-zinc-900 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-500 focus:border-cyan-400/50"
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
    <div className={`rounded-2xl border p-4 ${toneClasses[tone]}`}>
      <p className="text-xs uppercase tracking-[0.15em] opacity-75">{title}</p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
    </div>
  );
}

function EvidenceCard({ title, rows, chips, chipLabel, footerItems, footerLabel, accent = "cyan" }) {
  const accentBar = accent === "violet" ? "bg-violet-400" : "bg-cyan-400";

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/20">
      <div className="mb-5 flex items-center gap-3">
        <div className={`h-8 w-1 rounded-full ${accentBar}`} />
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>

      <div className="space-y-3">
        {rows.length ? (
          rows.map(([label, value]) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-zinc-900/70 px-4 py-3">
              <div className="text-xs uppercase tracking-[0.15em] text-zinc-500">{label}</div>
              <div className="mt-1 text-sm text-zinc-200">{value}</div>
            </div>
          ))
        ) : (
          <div className="text-sm text-zinc-500">No results yet</div>
        )}
      </div>

      <div className="mt-5">
        <div className="mb-2 text-xs uppercase tracking-[0.15em] text-zinc-500">{chipLabel}</div>
        <div className="flex flex-wrap gap-2">
          {chips.length ? (
            chips.map((chip) => (
              <span key={chip} className="rounded-full border border-white/10 bg-zinc-900 px-3 py-1 text-sm text-zinc-300">
                {chip}
              </span>
            ))
          ) : (
            <span className="text-sm text-zinc-500">None detected</span>
          )}
        </div>
      </div>

      <div className="mt-5">
        <div className="mb-2 text-xs uppercase tracking-[0.15em] text-zinc-500">{footerLabel}</div>
        <div className="space-y-2">
          {footerItems.length ? (
            footerItems.map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-zinc-900/70 px-4 py-3 text-sm text-zinc-300">
                {item}
              </div>
            ))
          ) : (
            <div className="text-sm text-zinc-500">None detected</div>
          )}
        </div>
      </div>
    </div>
  );
}