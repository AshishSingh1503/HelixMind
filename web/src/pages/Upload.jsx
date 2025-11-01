import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { analysisAPI } from '../services/api';
import toast from 'react-hot-toast';
import { Upload as UploadIcon, FileText, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [uploading, setUploading] = useState(false);
  const [analysisId, setAnalysisId] = useState(null);
  const navigate = useNavigate();

  const onDrop = async (acceptedFiles) => {
    console.log('🔍 Upload: onDrop triggered');
    console.log('📁 Files received:', acceptedFiles);
    
    const file = acceptedFiles[0];
    
    if (!file) {
      console.error('❌ No file received');
      toast.error('No file selected');
      return;
    }
    
    console.log('📄 File details:', {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified
    });
    
    if (!file.name.endsWith('.vcf')) {
      console.error('❌ Invalid file type:', file.name);
      toast.error('Please upload a VCF file');
      return;
    }

    setUploading(true);
    console.log('⏳ Starting upload...');
    
    try {
      console.log('🚀 Calling API upload...');
      const response = await analysisAPI.upload(file);
      console.log('✅ Upload response:', response);
      console.log('📊 Response data:', response.data);
      
      const { analysis_id } = response.data;
      console.log('🎯 Analysis ID:', analysis_id);
      
      setAnalysisId(analysis_id);
      toast.success('File uploaded successfully! Analysis started.');
      
      // Redirect to results page after a delay
      setTimeout(() => {
        console.log('🔄 Redirecting to results page...');
        navigate(`/results/${analysis_id}`);
      }, 2000);
      
    } catch (error) {
      console.error('❌ Upload error:', error);
      console.error('❌ Error response:', error.response);
      console.error('❌ Error data:', error.response?.data);
      console.error('❌ Error status:', error.response?.status);
      console.error('❌ Error message:', error.message);
      
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
      console.log('✅ Upload process finished');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.vcf']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Upload Genomic Data
        </h1>
        <p className="text-gray-600">
          Upload your VCF file to start genetic disease risk analysis
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Upload Area */}
        <div className="card">
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-primary-400'
            }`}
          >
            <input {...getInputProps()} />
            <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            
            {uploading ? (
              <div>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  Uploading...
                </p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-primary-600 h-2 rounded-full animate-pulse w-1/2"></div>
                </div>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop your VCF file here' : 'Drag & drop your VCF file'}
                </p>
                <p className="text-gray-600 mb-4">
                  or click to browse files
                </p>
                <button className="btn-primary">
                  Select File
                </button>
              </div>
            )}
          </div>

          {analysisId && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium">
                ✅ Analysis started! ID: {analysisId}
              </p>
              <p className="text-green-600 text-sm mt-1">
                Redirecting to results page...
              </p>
            </div>
          )}
        </div>

        {/* Information Panel */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <FileText className="h-5 w-5 mr-2 text-primary-600" />
              File Requirements
            </h3>
            <ul className="space-y-2 text-gray-600">
              <li>• File format: VCF (.vcf)</li>
              <li>• Maximum size: 100MB</li>
              <li>• Standard VCF format required</li>
              <li>• Human genome data only</li>
            </ul>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <AlertCircle className="h-5 w-5 mr-2 text-warning-500" />
              Privacy & Security
            </h3>
            <ul className="space-y-2 text-gray-600">
              <li>• All data processed locally</li>
              <li>• Secure encrypted storage</li>
              <li>• No data sharing with third parties</li>
              <li>• Full data deletion available</li>
            </ul>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold mb-3">Analysis Process</h3>
            <div className="space-y-3">
              <div className="flex items-center">
                <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                  1
                </div>
                <span className="text-gray-700">Variant extraction</span>
              </div>
              <div className="flex items-center">
                <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                  2
                </div>
                <span className="text-gray-700">Disease annotation</span>
              </div>
              <div className="flex items-center">
                <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                  3
                </div>
                <span className="text-gray-700">ML risk prediction</span>
              </div>
              <div className="flex items-center">
                <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3">
                  4
                </div>
                <span className="text-gray-700">Report generation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Upload;