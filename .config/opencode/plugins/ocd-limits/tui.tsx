import { Plugin } from "@opencode/plugin/tui";
import { createSignal } from "solid-js";
import { readFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";

const URL = "https://opencode.ai/zen/go/v1/usage";
const POLL_MS = 60 * 60 * 1000;

async function loadKey(): Promise<string> {
  const env = (globalThis as any)?.process?.env;
  if (env?.OCD_KEY) return env.OCD_KEY;
  if (env?.OPENCODE_GO_KEY) return env.OPENCODE_GO_KEY;
  const candidates = [
    join(homedir(), ".local/share/opencode/auth.json"),
    ...(env?.XDG_DATA_HOME
      ? [join(env.XDG_DATA_HOME, "opencode/auth.json")]
      : []),
  ];
  for (const p of candidates) {
    try {
      const raw = await readFile(p, "utf8");
      const key = JSON.parse(raw)?.["opencode-go"]?.key;
      if (key) return key;
    } catch {}
  }
  return "";
}

type Usage = { roll?: number; week?: number; mon?: number; left: string };

function formatLeft(resetsAt?: string): string {
  if (!resetsAt) return "";
  const ms = Date.parse(resetsAt) - Date.now();
  const s = Math.max(0, Math.floor(ms / 1000));
  if (s >= 86400) return `${String(Math.floor(s / 86400)).padStart(2, " ")}d`;
  return `${String(Math.floor(s / 3600)).padStart(2, " ")}h`;
}

async function fetchUsage(): Promise<Usage | null> {
  const key = await loadKey();
  if (!key) return null;
  try {
    const res = await fetch(URL, {
      headers: { Authorization: `Bearer ${key}` },
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) return null;
    const j: any = await res.json();
    const toNum = (v: unknown) => (typeof v === "number" ? v : undefined);
    return {
      roll: toNum(j?.usage?.rolling?.percent),
      week: toNum(j?.usage?.weekly?.percent),
      mon: toNum(j?.usage?.monthly?.percent),
      left: formatLeft(j?.usage?.monthly?.resetsAt),
    };
  } catch {
    return null;
  }
}

export default Plugin.define({
  id: "ocd-limits",
  setup(ctx) {
    const [label, setLabel] = createSignal("…");
    const [fg, setFg] = createSignal(ctx.theme.text.muted);

    const fmt = (v?: number) => (v === undefined ? "--" : `${v}%`);

    async function refresh() {
      const u = await fetchUsage();
      if (
        !u ||
        (u.roll === undefined && u.week === undefined && u.mon === undefined)
      ) {
        setLabel("--");
        setFg(ctx.theme.text.muted);
        return;
      }
      setFg(ctx.theme.text.muted);
      const parts = [fmt(u.roll), fmt(u.week), fmt(u.mon)].join(" ");
      const left = u.left.trim();
      setLabel(left ? `${parts} (${left})` : parts);
    }

    void refresh();
    const timer = setInterval(() => void refresh(), POLL_MS);

    ctx.ui.slot({
      append: "prompt.footer.status",
      render: (input: any) => {
        try {
          if ((ctx.ui.router.current() as any)?.type === "home")
            return null as any;
        } catch {}
        try {
          if (
            input &&
            typeof input === "object" &&
            "sessionID" in input &&
            !(input as any).sessionID
          )
            return null as any;
        } catch {}
        return (
          <text fg={fg()} wrapMode="none" truncate={true}>
            {label()}
          </text>
        );
      },
    });

    ctx.ui.slot({
      replace: "home.footer",
      render: () => (
        <box flexDirection="row" gap={2} paddingLeft={2} paddingRight={1}>
          <box flexGrow={1} flexShrink={1} minWidth={0}>
            <text fg={fg()} wrapMode="none" truncate={true}>
              {label()}
            </text>
          </box>
          <text fg={ctx.theme.text.muted} wrapMode="none">
            v{ctx.app.version}
          </text>
        </box>
      ),
    });

    return () => clearInterval(timer);
  },
});
