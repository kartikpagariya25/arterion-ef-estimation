// Per-site settings for the accounts UI (auth.js, history.js).
window.ARTERION_APP = {
  slug: "ef-estimation",
  name: "Arterion EF Console",
  home: "index.html",
  graphic: {type:"rings", colors:["#3a6df0","#f0a070"]},
  tasks: {
    "ef-estimation": "Ejection fraction"
  },
  // One-line summary of a saved result, shown at the top of its details.
  headline: function (r) {
    return 'EF ' + r.ejection_fraction + '%, ' + String(r.classification || '').replace(/_/g, ' ');
  },
};
