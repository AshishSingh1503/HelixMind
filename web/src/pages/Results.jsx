import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import toast from 'react-hot-toast';
import { FileText, AlertCircle, CheckCircle, Clock, XCircle, ArrowLeft, Download } from 'lucide-react';

const Results = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('📊 Results: Loading analysis ID:', id);
    fetchAnalysis();
    
    // Poll for updates if analysis is pending or processing
    const interval = setInterval(() => {
      if (analysis?.status === 'pending' || analysis?.status === 'processing') {
        console.log('🔄 Results: Polling for updates...');
        fetchAnalysis();
      }
    }, 3000); // Poll every 3 seconds

    return () => clearInterval(interval);
  }, [id]);

  const fetchAnalysis = async () => {
    try {
      console.log('📤 Results: Fetching analysis...');
      const response = await analysisAPI.getResult(id);
      console.log('✅ Results: Analysis data received:', response.data);
      
      // Handle both _id and id fields
      const analysisData = {
        ...response.data,
        id: response.data.id || response.data._id
      };
      
      setAnalysis(analysisData);
      setLoading(false);
    } catch (error) {
      console.error('❌ Results: Error fetching analysis:', error);
      console.error('❌ Results: Error response:', error.response);
      setError(error.response?.data?.detail || 'Failed to load analysis results');
      setLoading(false);
      toast.error('Failed to load results');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case 'processing':
        return <Clock className="h-6 w-6 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-6 w-6 text-red-500" />;
      default:
        return <Clock className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getRiskColor = (risk) => {
    const colors = {
      low: 'text-green-600',
      medium: 'text-yellow-600',
      high: 'text-red-600'
    };
    return colors[risk] || 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading analysis results...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-12 px-4">
        <div className="card text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-900 mb-2">Error Loading Results</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button onClick={() => navigate('/history')} className="btn-primary">
            View History
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-12 px-4">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => navigate('/history')}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-5 w-5 mr-2" />
          Back to History
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Analysis Results
            </h1>
            <p className="text-gray-600">
              Analysis ID: {id}
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            {getStatusIcon(analysis.status)}
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(analysis.status)}`}>
              {analysis.status.charAt(0).toUpperCase() + analysis.status.slice(1)}
            </span>
          </div>
        </div>
      </div>

      {/* Processing Status */}
      {(analysis.status === 'pending' || analysis.status === 'processing') && (
        <div className="card mb-6 bg-blue-50 border-blue-200">
          <div className="flex items-center">
            <Clock className="h-6 w-6 text-blue-600 animate-pulse mr-3" />
            <div>
              <h3 className="font-semibold text-blue-900">Analysis in Progress</h3>
              <p className="text-blue-700 text-sm">
                Your genomic data is being analyzed. This page will update automatically.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Failed Status */}
      {analysis.status === 'failed' && (
        <div className="card mb-6 bg-red-50 border-red-200">
          <div className="flex items-center">
            <XCircle className="h-6 w-6 text-red-600 mr-3" />
            <div>
              <h3 className="font-semibold text-red-900">Analysis Failed</h3>
              <p className="text-red-700 text-sm">
                {analysis.error_message || 'An error occurred during analysis. Please try uploading again.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* File Information */}
      <div className="card mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <FileText className="h-5 w-5 mr-2 text-primary-600" />
          File Information
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Filename</p>
            <p className="font-medium">{analysis.filename || analysis.vcf_file || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Upload Date</p>
            <p className="font-medium">
              {analysis.created_at ? new Date(analysis.created_at).toLocaleString() : 'N/A'}
            </p>
          </div>
          {analysis.completed_at && (
            <div>
              <p className="text-sm text-gray-600">Completed Date</p>
              <p className="font-medium">
                {new Date(analysis.completed_at).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Results - Only show if completed */}
      {analysis.status === 'completed' && (
        <>
          {/* Summary Cards */}
          <div className="grid md:grid-cols-4 gap-6 mb-6">
            <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
              <p className="text-sm text-gray-600 mb-1">Total Variants</p>
              <p className="text-3xl font-bold text-blue-900">
                {analysis.variants_analyzed || analysis.total_variants || 0}
              </p>
            </div>
            
            <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
              <p className="text-sm text-gray-600 mb-1">High Risk Variants</p>
              <p className="text-3xl font-bold text-yellow-900">
                {analysis.high_risk_variants || 0}
              </p>
            </div>
            
            <div className="card bg-gradient-to-br from-red-50 to-red-100">
              <p className="text-sm text-gray-600 mb-1">Pathogenic Variants</p>
              <p className="text-3xl font-bold text-red-900">
                {analysis.pathogenic_variants || 0}
              </p>
            </div>
            
            <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
              <p className="text-sm text-gray-600 mb-1">Risk Classification</p>
              <p className={`text-3xl font-bold ${getRiskColor(analysis.risk_classification)}`}>
                {analysis.risk_classification ? analysis.risk_classification.toUpperCase() : 'N/A'}
              </p>
            </div>
          </div>

          {/* Risk Probability */}
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">Risk Assessment</h2>
            <div className="mb-2">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">Risk Probability</span>
                <span className="text-sm font-bold text-gray-900">
                  {analysis.risk_probability ? (analysis.risk_probability * 100).toFixed(1) : 0}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full ${
                    (analysis.risk_probability || 0) < 0.3 ? 'bg-green-500' :
                    (analysis.risk_probability || 0) < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${(analysis.risk_probability || 0) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Variants Table */}
          {analysis.top_variants && analysis.top_variants.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold mb-4">Top Identified Variants</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Chromosome
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Position
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Gene
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Risk Level
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Clinical Significance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Disease
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analysis.top_variants.map((variant, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {variant.chromosome}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {variant.position}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {variant.gene || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            variant.risk === 'HIGH' ? 'bg-red-100 text-red-800' :
                            variant.risk === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {variant.risk}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            variant.clnsig === 'Pathogenic' ? 'bg-red-100 text-red-800' :
                            variant.clnsig === 'Likely_pathogenic' ? 'bg-orange-100 text-orange-800' :
                            variant.clnsig === 'VUS' ? 'bg-gray-100 text-gray-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {variant.clnsig}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {variant.disease ? variant.disease.replace(/_/g, ' ') : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}

      {/* Actions */}
      <div className="mt-6 flex justify-between">
        <button
          onClick={() => navigate('/history')}
          className="btn-secondary"
        >
          View All Results
        </button>
        
        {analysis.status === 'completed' && (
          <button
            className="btn-primary flex items-center"
            onClick={async () => {
              try {
                toast.loading('Generating report...', { id: 'download' });
                await analysisAPI.downloadReport(analysis.id);
                toast.success('Report downloaded successfully!', { id: 'download' });
              } catch (error) {
                console.error('Error downloading report:', error);
                toast.error('Failed to download report', { id: 'download' });
              }
            }}
          >
            <Download className="h-5 w-5 mr-2" />
            Download Report
          </button>
        )}
      </div>
    </div>
  );
};

export default Results;
