import React, { useState } from 'react';
import axios from 'axios';

interface SearchResult {
  _id: string;
  _source: {
    title: string;
    timestamp: string;
    location: string;
    summary: string;
    url: string;
  };
}

export default function PersonSearch() {
  const [name, setName] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    setResults([]); // Reset results before searching
  
    try {
      const res = await axios.post<{ hits: { hits: SearchResult[] } }>(
        'http://localhost:5000/api/search_person',
        { name }
      );
  
      console.log("API Response:", res.data); // ✅ Log full response
  
      // ✅ Ensure correct array extraction
      if (res.data?.hits?.length > 0) {
        console.log(res.data?.hits?.length);
        setResults(res.data.hits); // ✅ Now setting correct results
      } else {
        console.warn("No results found in API response.");
        setResults([]);
      }
    } catch (err) {
      console.error('Axios error:', err);
      setError('Error fetching results.');
    } finally {
      setLoading(false);
    }
  };
  
  

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded shadow">
      <h2 className="text-2xl font-bold mb-4">Person Search</h2>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Enter person's name..."
        className="w-full border p-2 rounded mb-3"
      />
      <button
        onClick={handleSearch}
        disabled={loading || !name.trim()}
        className="bg-blue-600 text-white px-4 py-2 rounded"
      >
        {loading ? 'Searching...' : 'Search'}
      </button>

      {error && <div className="text-red-500 mt-3">{error}</div>}

      <div className="mt-4 space-y-3">
        {results && results.length > 0 ? (
          results.map((item) => (
            <div key={item._id} className="p-4 bg-gray-50 rounded shadow-sm">
              <h3 className="font-semibold">{item._source.title}</h3>
              <p><strong>Date:</strong> {item._source.timestamp}</p>
              <p><strong>Location:</strong> {item._source.location}</p>
              <p><strong>Summary:</strong> {item._source.summary}</p>
              <a
                href={item._source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 underline"
              >
                Read full article
              </a>
            </div>
          ))
        ) : (
          !loading && <div className="text-gray-500">No results found.</div>
        )}
      </div>
    </div>
  );
}
