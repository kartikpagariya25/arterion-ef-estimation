(() => {
  const $ = (id) => document.getElementById(id);
  const API = window.API_BASE.replace(/\/$/, "");
  const MAX = 80, CX = 120, CY = 124, R = 90;
  const LABEL = { normal: "Normal", mildly_reduced: "Mildly reduced", moderately_reduced: "Moderately reduced", severely_reduced: "Severely reduced" };
  const BAND_CLASS = { normal: "norm", mildly_reduced: "mild", moderately_reduced: "mod", severely_reduced: "sev" };

  /* ---------- gauge geometry ---------- */
  const pt = (v) => {
    const a = ((-180 + (Math.min(v, MAX) / MAX) * 180) * Math.PI) / 180;
    return [CX + R * Math.cos(a), CY + R * Math.sin(a)];
  };
  const arc = (a, b) => { const [x1, y1] = pt(a), [x2, y2] = pt(b); return `M${x1.toFixed(2)} ${y1.toFixed(2)}A${R} ${R} 0 0 1 ${x2.toFixed(2)} ${y2.toFixed(2)}`; };
  const gap = 0.6;
  [["b-sev", 0, 30], ["b-mod", 30, 45], ["b-mild", 45, 55], ["b-norm", 55, MAX]].forEach(([c, a, b]) =>
    document.querySelector("." + c).setAttribute("d", arc(a + (a ? gap : 0), b - (b < MAX ? gap : 0))));
  const NS = "http://www.w3.org/2000/svg";
  [0, 30, 45, 55, 80].forEach((v) => {
    const a = ((-180 + (v / MAX) * 180) * Math.PI) / 180, r = R + 20;
    const t = document.createElementNS(NS, "text");
    t.setAttribute("x", (CX + r * Math.cos(a)).toFixed(1)); t.setAttribute("y", (CY + r * Math.sin(a) + 3).toFixed(1));
    t.setAttribute("text-anchor", v === 0 ? "end" : v === 80 ? "start" : "middle"); t.setAttribute("class", "tick");
    t.textContent = v === 80 ? "80+" : v; $("gaugeSvg").appendChild(t);
  });
  const setNeedle = (v) => ($("needle").style.transform = `rotate(${-90 + (Math.min(Math.max(v, 0), MAX) / MAX) * 180}deg)`);

  /* ---------- status ---------- */
  (async () => {
    const el = $("status");
    try {
      if (!(await fetch(API + "/health", { cache: "no-store" })).ok) throw 0;
      el.className = "status ok"; el.lastElementChild.textContent = "API online";
    } catch {
      el.className = "status bad"; el.lastElementChild.textContent = "API offline · " + API;
    }
  })();

  /* ---------- input ---------- */
  const drop = $("drop");
  ["dragenter", "dragover"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((e) => drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", (e) => e.dataTransfer.files[0] && analyse(e.dataTransfer.files[0]));
  $("file").addEventListener("change", (e) => e.target.files[0] && analyse(e.target.files[0]));
  $("reset").addEventListener("click", reset);
  $("video").addEventListener("error", () => { if ($("video").getAttribute("src")) { show($("video"), false); show($("nopreview"), true); } });

  const show = (el, on) => (el.hidden = !on);
  const setError = (m) => { $("error").textContent = m || ""; show($("error"), !!m); };

  function reset() {
    const v = $("video"); v.pause(); if (v.src) URL.revokeObjectURL(v.src); v.removeAttribute("src"); v.load();
    show(v, false); show($("nopreview"), false); show(drop, true); show($("reset"), false); show($("fileChip"), false); show($("notice"), false); setError("");
    $("file").value = ""; $("ef").textContent = "—"; setNeedle(0);
    $("classChip").textContent = "Waiting for study"; $("classChip").style.cssText = "";
    $("summary").textContent = "Results appear here once a study is analysed.";
    show($("spread"), false); show($("facts"), false);
    document.querySelectorAll(".band-card").forEach((c) => c.classList.remove("on"));
  }

  async function post(path, body, isForm) {
    const r = await fetch(API + path, { method: "POST", headers: isForm ? undefined : { "Content-Type": "application/json" }, body: isForm ? body : JSON.stringify(body) });
    let j = null; try { j = await r.json(); } catch {}
    if (!r.ok) throw new Error((j && j.detail) || `Request failed (${r.status})`);
    return j;
  }

  async function analyse(file) {
    setError(""); show($("notice"), false);
    if (!file.type.startsWith("video/") && !/\.(avi|mp4|mov|mkv)$/i.test(file.name)) {
      return setError("That does not look like a video. Choose an AVI or MP4 echocardiogram.");
    }
    const v = $("video");
    show($("nopreview"), false); v.src = URL.createObjectURL(file); show(v, true); show(drop, false);
    $("fileChip").textContent = file.name; show($("fileChip"), true); show($("reset"), true);
    show($("busy"), true); $("busyText").textContent = "Uploading";
    try {
      const fd = new FormData(); fd.append("file", file);
      const { file_url } = await post("/uploads", fd, true);
      $("busyText").textContent = "Estimating EF";
      const res = await post("/ef-estimation/predict", { file_url });
      render(res);
      v.play().catch(() => {});
    } catch (e) {
      setError(e.message === "Failed to fetch" ? `Cannot reach the API at ${API}. Is the backend running?` : e.message);
      show(v, false); show($("nopreview"), false); show(drop, true); show($("fileChip"), false); show($("reset"), false);
    } finally {
      show($("busy"), false);
    }
  }

  function render(r) {
    if (r.classification === "unknown") {
      show($("notice"), true);
      $("notice").innerHTML = "The model weights are not installed, so no estimate was produced. Run <code>scripts/fetch_weights</code> (or place <code>ef_model.onnx</code> in <code>backend/app/ef_estimation/weights/</code>) and restart the API.";
      return;
    }
    const ef = r.ejection_fraction;
    setNeedle(ef);
    // count-up
    const t0 = performance.now();
    const tick = (t) => { const k = Math.min((t - t0) / 1100, 1); $("ef").textContent = (ef * (1 - Math.pow(1 - k, 3))).toFixed(1); if (k < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);

    const cls = BAND_CLASS[r.classification];
    const chip = $("classChip");
    chip.textContent = LABEL[r.classification];
    chip.style.background = `var(--${cls})`; chip.style.color = "#fff";
    $("summary").textContent = r.summary;
    document.querySelectorAll(".band-card").forEach((c) => c.classList.toggle("on", c.classList.contains(cls)));

    const [lo, hi] = r.ef_range;
    show($("spread"), true);
    $("spreadTxt").textContent = r.clips_used > 1 ? `${lo.toFixed(1)} – ${hi.toFixed(1)} %` : "single clip";
    const f = $("spreadFill"); f.style.left = (lo / MAX) * 100 + "%"; f.style.width = Math.max(((hi - lo) / MAX) * 100, 1.5) + "%";
    const width = hi - lo;
    $("spreadNote").textContent = r.clips_used <= 1 ? "Video too short for several windows; one clip was scored."
      : width > 10 ? "The windows disagree noticeably — image quality or motion may be limiting the estimate."
      : "The scored windows agree closely.";
    show($("facts"), true); $("fFrames").textContent = r.frames ?? "—"; $("fClips").textContent = r.clips_used;
  }
  setNeedle(0);
})();
