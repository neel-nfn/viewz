function getTitle() {
  const el = document.querySelector("h1.title") || document.querySelector("h1.ytd-watch-metadata");
  return el ? el.textContent.trim() : document.title;
}

function injectBadge(text) {
  let host = document.querySelector("#owner") || document.body;
  const badge = document.createElement("div");
  badge.style.cssText = "position:relative;display:inline-flex;margin-left:8px;padding:4px 8px;border-radius:9999px;background:#eee;font-size:12px;";
  badge.textContent = text;
  host.prepend(badge);
}

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "OUTLIER_RESULT") injectBadge(`Outlier ${msg.score}`);
});

chrome.runtime.sendMessage({ type: "NEED_TITLE", title: getTitle(), url: location.href });

