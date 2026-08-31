(() => {
  const form = document.querySelector("[data-docs-search]");
  const input = document.querySelector("[data-docs-search-input]");
  const status = document.querySelector("[data-docs-search-status]");
  const results = document.querySelector("[data-docs-search-results]");
  if (!form || !input || !status || !results) return;

  const normalize = (value) => value.toLocaleLowerCase().replace(/\s+/g, " ").trim();
  let recordsPromise;

  const records = () => {
    if (!recordsPromise) {
      recordsPromise = fetch("/docs/search.json", { credentials: "same-origin" })
        .then((response) => {
          if (!response.ok) throw new Error(`search index returned ${response.status}`);
          return response.json();
        });
    }
    return recordsPromise;
  };

  const clear = () => {
    while (results.firstChild) results.removeChild(results.firstChild);
  };

  const scoreRecord = (record, terms) => {
    const title = normalize(record.title);
    const description = normalize(record.description);
    const headings = normalize(record.headings.map((heading) => heading.title).join(" "));
    const project = normalize(record.project);
    const text = normalize(record.text);
    let score = 0;

    for (const term of terms) {
      if (!text.includes(term) && !title.includes(term) && !description.includes(term) &&
          !headings.includes(term) && !project.includes(term)) return 0;
      if (title.includes(term)) score += 12;
      if (title.startsWith(term)) score += 5;
      if (headings.includes(term)) score += 7;
      if (description.includes(term)) score += 4;
      if (project.includes(term)) score += 3;
      if (text.includes(term)) score += 1;
    }
    return score;
  };

  const resultNode = (record) => {
    const item = document.createElement("li");
    const heading = document.createElement("h2");
    const link = document.createElement("a");
    const description = document.createElement("p");
    const metadata = document.createElement("small");

    link.href = record.route;
    link.textContent = record.title;
    heading.appendChild(link);
    description.textContent = record.description;
    metadata.textContent = `${record.project} · ${record.group.replaceAll("-", " ")}`;
    item.append(heading, description, metadata);
    return item;
  };

  const search = async (query) => {
    const terms = normalize(query).split(" ").filter(Boolean);
    clear();
    if (!terms.length) {
      status.textContent = "Enter one or more terms.";
      return;
    }

    status.textContent = "Searching…";
    try {
      const index = await records();
      const matches = index
        .map((record) => ({ record, score: scoreRecord(record, terms) }))
        .filter((match) => match.score > 0)
        .sort((left, right) => right.score - left.score ||
          (left.record.route < right.record.route ? -1 : 1))
        .slice(0, 50);

      status.textContent = `${matches.length} ${matches.length === 1 ? "result" : "results"}.`;
      for (const match of matches) results.appendChild(resultNode(match.record));
    } catch (error) {
      status.textContent = "The search index could not be loaded.";
      console.error(error);
    }
  };

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const query = input.value.trim();
    const url = new URL(window.location.href);
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    window.history.replaceState(null, "", url);
    search(query);
  });

  const initial = new URL(window.location.href).searchParams.get("q") || "";
  input.value = initial;
  search(initial);
})();
