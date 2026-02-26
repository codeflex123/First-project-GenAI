const { useState } = React;

const AREAS = [
  { value: "", label: "Any area" },
  { value: "Bangalore", label: "Bangalore (any)" },
  { value: "Banashankari", label: "Banashankari" },
  { value: "Basavanagudi", label: "Basavanagudi" },
  { value: "Koramangala", label: "Koramangala" },
  { value: "Indiranagar", label: "Indiranagar" },
  { value: "Jayanagar", label: "Jayanagar" },
  { value: "HSR", label: "HSR" },
  { value: "Whitefield", label: "Whitefield" },
  { value: "MG Road", label: "MG Road" },
  { value: "Brigade Road", label: "Brigade Road" },
  { value: "Marathahalli", label: "Marathahalli" },
  { value: "Electronic City", label: "Electronic City" },
  { value: "JP Nagar", label: "JP Nagar" },
  { value: "BTM Layout", label: "BTM Layout" },
  { value: "Malleshwaram", label: "Malleshwaram" },
];

const CUISINES = [
  "",
  "North Indian",
  "South Indian",
  "Chinese",
  "Italian",
  "Pizza",
  "Fast Food",
  "Cafe",
  "Biryani",
  "Mexican",
  "Mughlai",
  "Rajasthani",
];

const RATINGS = ["", "3.5", "4.0", "4.5", "4.8"];

const PRICES = [
  { value: "", label: "Any price" },
  { value: "1", label: "Up to 400" },
  { value: "2", label: "400 – 800" },
  { value: "3", label: "800 – 1500" },
  { value: "4", label: "1500+" },
];

function App() {
  const [city, setCity] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [explanation, setExplanation] = useState("");
  const [results, setResults] = useState([]);

  const filteredLabel = [
    city && `Area: ${city}`,
    cuisine && `Cuisine: ${cuisine}`,
    minRating && `Min rating: ${minRating}`,
    maxPrice && `Max price band: ${maxPrice}`,
  ].filter(Boolean);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setExplanation("");
    setResults([]);
    setLoading(true);

    const payload = {
      city: city || null,
      cuisines: cuisine ? [cuisine] : null,
      min_rating: minRating ? parseFloat(minRating) : null,
      price_range: maxPrice ? parseInt(maxPrice, 10) : null,
    };

    try {
      const resp = await fetch("/api/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const text = await resp.text();
        setError(`Error ${resp.status}: ${text}`);
        return;
      }

      const data = await resp.json();
      setExplanation(data.explanation || "");
      setResults(Array.isArray(data.recommendations) ? data.recommendations : []);
    } catch (e) {
      console.error(e);
      setError("Network or server error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setCity("");
    setCuisine("");
    setMinRating("");
    setMaxPrice("");
    setExplanation("");
    setResults([]);
    setError("");
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="react-form">
        <div className="field">
          <label htmlFor="city-select">Area (Bangalore)</label>
          <select
            id="city-select"
            value={city}
            onChange={(e) => setCity(e.target.value)}
          >
            {AREAS.map((a) => (
              <option key={a.value || "any"} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="cuisine-select">Cuisine (optional)</label>
          <select
            id="cuisine-select"
            value={cuisine}
            onChange={(e) => setCuisine(e.target.value)}
          >
            {CUISINES.map((c) => (
              <option key={c || "any"} value={c}>
                {c || "Any cuisine"}
              </option>
            ))}
          </select>
        </div>

        <div className="field two-column">
          <div>
            <label htmlFor="rating-select">Minimum Rating (optional)</label>
            <select
              id="rating-select"
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
            >
              {RATINGS.map((r) => (
                <option key={r || "any"} value={r}>
                  {r || "Any rating"}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="price-select">Max price (for two, INR) (optional)</label>
            <select
              id="price-select"
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
            >
              {PRICES.map((p) => (
                <option key={p.value || "any"} value={p.value}>
                  {p.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading}>
            {loading ? "Getting recommendations..." : "Get Recommendations"}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={handleClear}
            disabled={loading}
          >
            Clear
          </button>
        </div>

        {filteredLabel.length > 0 && (
          <div className="filters-summary">
            <strong>Current filters:</strong> {filteredLabel.join(" • ")}
          </div>
        )}

        {error && <div className="status error">{error}</div>}
      </form>

      <section className="card results-card">
        <h2>Recommendations</h2>
        {explanation && <p id="explanation">{explanation}</p>}
        <div id="results">
          {results.length === 0 && !loading && !error && (
            <p>No restaurants matched the given filters.</p>
          )}
          {results.map((rec) => (
            <article key={rec.source_id} className="restaurant-card">
              <h3>{rec.name}</h3>
              <p>
                {rec.city || "Unknown area"} •{" "}
                {(rec.cuisines || []).join(", ") || "N/A"} •{" "}
                {rec.average_cost_for_two != null
                  ? `Cost for two: ${rec.average_cost_for_two}`
                  : "Cost N/A"}{" "}
                •{" "}
                {rec.rating != null
                  ? `${rec.rating.toFixed(1)} ⭐ (${rec.votes || 0} votes)`
                  : "No rating"}
              </p>
              <p>{rec.summary || ""}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

const rootEl = document.getElementById("root");
if (rootEl) {
  const root = ReactDOM.createRoot(rootEl);
  root.render(<App />);
}
