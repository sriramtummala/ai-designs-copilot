import { useState } from 'react';
import { Button, Card, Alert, PageSection } from '@ai-designops/ui';
import '@ai-designops/tokens/theme.css';
import './App.css';
import DsComparison from './DsComparison';

type View = 'form' | 'tokens'

function App() {
  const [view, setView] = useState<View>('form')
  const [formData, setFormData] = useState({
    pageType: 'landing_page',
    audience: 'developers',
    brand: 'brand_a',
    channel: 'web',
    notes: ''
  });
 
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Request Submitted:', formData);
    alert('Request captured! Check console for JSON.');
  };
 
  return (
    <div className="container">
      <header>
        <PageSection title="AI DesignOps Copilot">
          <p>Structured Page Generation Request</p>
        </PageSection>
        <nav style={{ display: 'flex', gap: 8, marginTop: 12 }}>
          <button onClick={() => setView('form')} style={{ fontWeight: view === 'form' ? 700 : 400 }}>Request form</button>
          <button onClick={() => setView('tokens')} style={{ fontWeight: view === 'tokens' ? 700 : 400 }}>Token comparison</button>
        </nav>
      </header>

      {view === 'tokens' ? <DsComparison /> : <main>
        <Card title="New Page Request">
          <Alert type="info">Fill out the form below to generate a page plan.</Alert>
          <form onSubmit={handleSubmit} className="request-form">
            <div className="form-group">
              <label>Page Type</label>
              <select 
                value={formData.pageType} 
                onChange={(e) => setFormData({...formData, pageType: e.target.value})}
              >
                <option value="landing_page">Landing Page</option>
                <option value="product_page">Product Page</option>
                <option value="blog_post">Blog Post</option>
              </select>
            </div>
 
            <div className="form-group">
              <label>Target Audience</label>
              <select 
                value={formData.audience} 
                onChange={(e) => setFormData({...formData, audience: e.target.value})}
              >
                <option value="developers">Developers</option>
                <option value="designers">Designers</option>
                <option value="marketers">Marketers</option>
              </select>
            </div>
 
            <div className="form-group">
              <label>Brand Identity</label>
              <select 
                value={formData.brand} 
                onChange={(e) => setFormData({...formData, brand: e.target.value})}
              >
                <option value="brand_a">Brand A (Corporate)</option>
                <option value="brand_b">Brand B (Modern/Tech)</option>
              </select>
            </div>
 
            <div className="form-group">
              <label>Channel</label>
              <select 
                value={formData.channel} 
                onChange={(e) => setFormData({...formData, channel: e.target.value})}
              >
                <option value="web">Web</option>
                <option value="mobile">Mobile App</option>
                <option value="email">Email</option>
              </select>
            </div>
 
            <div className="form-group">
              <label>Additional Notes</label>
              <textarea 
                placeholder="Enter specific requirements..."
                value={formData.notes}
                onChange={(e) => setFormData({...formData, notes: e.target.value})}
              />
            </div>
 
            <Button onClick={() => {}} type="submit">Generate Page Plan</Button>
          </form>
        </Card>
 
        <Card title="Request Preview">
          <pre>{JSON.stringify(formData, null, 2)}</pre>
        </Card>
      </main>}
    </div>
  );
}
 
export default App;
