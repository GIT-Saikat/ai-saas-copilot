import React, { useEffect, useState } from 'react';
import { Wifi, WifiOff, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Badge } from './ui/badge';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import apiService from '../services/api';

export const ConnectionStatus: React.FC = () => {
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkConnection = async () => {
      setIsChecking(true);
      setError(null);
      
      try {
        const health = await apiService.healthCheck();
        setIsConnected(health.status === 'healthy' || health.status === 'degraded');
        setError(null);
      } catch (err: any) {
        setIsConnected(false);
        setError(err.message || 'Cannot connect to backend server');
      } finally {
        setIsChecking(false);
      }
    };

    // Check immediately
    checkConnection();

    // Check every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isChecking) {
    return (
      <Badge variant="outline" className="gap-2">
        <Loader2 className="h-3 w-3 animate-spin" />
        Connecting...
      </Badge>
    );
  }

  if (isConnected) {
    return (
      <Badge variant="outline" className="gap-2 bg-green-50 border-green-300 text-green-800 dark:bg-green-900/20 dark:text-green-400">
        <Wifi className="h-3 w-3" />
        <CheckCircle2 className="h-3 w-3" />
        Connected
      </Badge>
    );
  }

  return (
    <div className="space-y-2">
      <Badge variant="outline" className="gap-2 bg-red-50 border-red-300 text-red-800 dark:bg-red-900/20 dark:text-red-400">
        <WifiOff className="h-3 w-3" />
        <XCircle className="h-3 w-3" />
        Disconnected
      </Badge>
      {error && (
        <Alert variant="destructive" className="mt-2">
          <AlertTitle>Backend Connection Failed</AlertTitle>
          <AlertDescription>
            {error}
            <br />
            <span className="text-xs mt-1 block">
              Make sure the backend server is running on http://localhost:8000
            </span>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
};

