// Serverless function to proxy Spoonacular API calls
// This keeps the API key secure on the server side

export default async function handler(req, res) {
    // Enable CORS for Telegram WebApp
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    // Only allow GET requests
    if (req.method !== 'GET') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { query, diet } = req.query;
    // Check both possible env var names
    const apiKey = process.env.SPOONACULAR_API_KEY || process.env.YOUR_SPOONACULAR_API_KEY;

    if (!apiKey || apiKey === 'YOUR_SPOONACULAR_API_KEY') {
        return res.status(500).json({ error: 'API key not configured' });
    }

    if (!query) {
        return res.status(400).json({ error: 'Query parameter is required' });
    }

    try {
        const dietParam = diet ? `&diet=${diet}` : '';
        const url = `https://api.spoonacular.com/recipes/complexSearch?query=${encodeURIComponent(query)}${dietParam}&apiKey=${apiKey}&number=1&addRecipeInformation=true`;

        const response = await fetch(url);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Spoonacular API error: ${response.status} - ${errorText}`);
        }

        const data = await response.json();
        res.status(200).json(data);
    } catch (error) {
        console.error('Error fetching recipe:', error);
        res.status(500).json({ error: error.message });
    }
}

