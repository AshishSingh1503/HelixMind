import React from 'react';
import { Link } from 'react-router-dom';
import { Dna, Shield, BarChart3, Users, Upload, Brain } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            🧬 GenomeGuard
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            AI-Powered Genetic Disease Predictor with Enterprise-Grade Security
          </p>
          <p className="text-lg mb-10 max-w-4xl mx-auto opacity-90">
            Analyze your genomic data to predict risks for cancer, Alzheimer's, and inherited disorders 
            using advanced machine learning and secure backend infrastructure.
          </p>
          <div className="space-x-4">
            <Link to="/register" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Get Started
            </Link>
            <Link to="/login" className="border-2 border-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary-600 transition-colors">
              Login
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <Shield className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">Secure Backend</h3>
              <p className="text-gray-600">JWT authentication, MongoDB storage, and enterprise-grade security</p>
            </div>
            <div className="text-center">
              <Brain className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">AI Analysis</h3>
              <p className="text-gray-600">Machine learning models for accurate disease risk prediction</p>
            </div>
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">Interactive Reports</h3>
              <p className="text-gray-600">Comprehensive visualizations and detailed analysis results</p>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="font-semibold mb-2">1. Register</h3>
              <p className="text-gray-600">Create secure account</p>
            </div>
            <div className="text-center">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Upload className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="font-semibold mb-2">2. Upload VCF</h3>
              <p className="text-gray-600">Upload genomic data file</p>
            </div>
            <div className="text-center">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="font-semibold mb-2">3. AI Analysis</h3>
              <p className="text-gray-600">Automated processing</p>
            </div>
            <div className="text-center">
              <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="font-semibold mb-2">4. View Results</h3>
              <p className="text-gray-600">Interactive dashboard</p>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Diseases */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Supported Genetic Variants</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card text-center">
              <h3 className="font-semibold text-lg mb-2">BRCA1/BRCA2</h3>
              <p className="text-gray-600">Breast & Ovarian Cancer</p>
            </div>
            <div className="card text-center">
              <h3 className="font-semibold text-lg mb-2">APOE</h3>
              <p className="text-gray-600">Alzheimer's Disease</p>
            </div>
            <div className="card text-center">
              <h3 className="font-semibold text-lg mb-2">TP53</h3>
              <p className="text-gray-600">Li-Fraumeni Syndrome</p>
            </div>
            <div className="card text-center">
              <h3 className="font-semibold text-lg mb-2">More</h3>
              <p className="text-gray-600">Expanding database</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Dna className="h-6 w-6" />
            <span className="text-lg font-semibold">GenomeGuard</span>
          </div>
          <p className="text-gray-400 mb-4">
            Enterprise-grade genetic disease prediction platform
          </p>
          <p className="text-sm text-gray-500">
            © 2024 GenomeGuard. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;