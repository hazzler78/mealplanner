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
        // First, search for recipes
        const searchUrl = `https://api.spoonacular.com/recipes/complexSearch?query=${encodeURIComponent(query)}${dietParam}&apiKey=${apiKey}&number=1&addRecipeInformation=true`;

        const searchResponse = await fetch(searchUrl);
        
        if (!searchResponse.ok) {
            const errorText = await searchResponse.text();
            throw new Error(`Spoonacular API error: ${searchResponse.status} - ${errorText}`);
        }

        const searchData = await searchResponse.json();
        
        // If we found a recipe, get detailed information including step-by-step instructions
        if (searchData.results && searchData.results.length > 0) {
            const recipeId = searchData.results[0].id;
            
            // Fetch detailed recipe information
            const detailUrl = `https://api.spoonacular.com/recipes/${recipeId}/information?apiKey=${apiKey}&includeNutrition=false`;
            const detailResponse = await fetch(detailUrl);
            
            // Fetch analyzed instructions separately (step-by-step)
            const analyzedUrl = `https://api.spoonacular.com/recipes/${recipeId}/analyzedInstructions?apiKey=${apiKey}`;
            const analyzedResponse = await fetch(analyzedUrl);
            
            let detailData = {};
            let analyzedInstructions = null;
            
            if (detailResponse.ok) {
                detailData = await detailResponse.json();
            }
            
            if (analyzedResponse.ok) {
                const analyzedData = await analyzedResponse.json();
                analyzedInstructions = analyzedData.length > 0 ? analyzedData : null;
            }
            
            // Merge detailed info with search results
            const mergedRecipe = {
                ...searchData.results[0],
                ...detailData,
                // Prefer detailed instructions if available
                instructions: detailData.instructions || searchData.results[0].instructions || '',
                analyzedInstructions: analyzedInstructions,
                readyInMinutes: detailData.readyInMinutes || null,
                servings: detailData.servings || null,
                summary: detailData.summary || null
            };
            
            return res.status(200).json({
                ...searchData,
                results: [mergedRecipe]
            });
        }
        
        // Return search results even if detail fetch fails
        res.status(200).json(searchData);
    } catch (error) {
        console.error('Error fetching recipe:', error);
        res.status(500).json({ error: error.message });
    }
}

