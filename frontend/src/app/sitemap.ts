export default function sitemap() {
  return [
    { url: 'https://pmis-demo.vercel.app', lastModified: new Date(), changeFrequency: 'weekly', priority: 1.0 },
    { url: 'https://pmis-demo.vercel.app/login', lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: 'https://pmis-demo.vercel.app/recommendations', lastModified: new Date(), changeFrequency: 'daily', priority: 0.9 },
  ]
}
