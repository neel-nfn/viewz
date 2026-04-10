async function scoreIdea(title, url) {
  try {
    const orgId = "";
    const channelId = "";
    const res = await fetch("http://localhost:8000/api/v1/research/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ org_id: orgId, channel_id: channelId, title, url })
    });
    return await res.json();
  } catch (e) { return null; }
}

chrome.runtime.onMessage.addListener(async (msg, sender) => {
  if (msg.type === "NEED_TITLE") {
    const data = await scoreIdea(msg.title, msg.url);
    if (data && sender.tab && sender.tab.id) {
      chrome.tabs.sendMessage(sender.tab.id, { type: "OUTLIER_RESULT", score: data.score });
    }
  }
});

