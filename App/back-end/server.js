const express = require('express');
const cors = require('cors');
const { Client } = require('@elastic/elasticsearch');

const app = express();
const PORT = 5000;

app.use(express.json());
app.use(cors());

const client = new Client({
  node: 'https://d055bd66cb6340cbaaf1e9955db841f7.us-central1.gcp.cloud.es.io:443',
  auth: {
    username: 'elastic',
    password: 'uLko2QHYccbOJXVhUO1vq7f0'
  }
});

// Search specifically in "persons" array
app.post('/api/search_person', async (req, res) => {
  const { name } = req.body;

  try {
    const result = await client.search({
      index: 'news_articles_data',
      query: {
        term: {
          "persons.keyword": name
        }
      }
    });
    res.json(result.hits);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Elasticsearch query failed' });
  }
});

app.listen(PORT, () => {
  console.log('Server running on port '+ PORT);
});
