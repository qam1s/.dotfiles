import { Plugin } from "@opencode/plugin/tui";

const SETTLE_DELAYS_MS = [0, 60, 180, 400, 800];

export default Plugin.define({
  id: "session-fresh",
  setup(context) {
    let stopped = false;

    const activeSessionID = () => {
      try {
        const route = context.ui.router.current();
        return route.type === "session" ? route.sessionID : undefined;
      } catch {
        return undefined;
      }
    };

    const closeTabs = (keepActive: boolean) => {
      if (!context.ui.tabs.enabled()) return;
      const keep = keepActive ? activeSessionID() : undefined;
      for (const tab of context.ui.tabs.list()) {
        if (keep && tab.sessionID === keep) continue;
        if (keepActive && tab.active) continue;
        context.ui.tabs.close(tab.sessionID);
      }
    };

    const timers = SETTLE_DELAYS_MS.map((delay) =>
      setTimeout(() => {
        if (!stopped) closeTabs(true);
      }, delay),
    );

    return () => {
      stopped = true;
      for (const timer of timers) clearTimeout(timer);
      closeTabs(false);
    };
  },
});
