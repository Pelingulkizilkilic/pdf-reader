import { useState, useEffect } from "react";

const useBackendStatus = () => {
  const [isBackendOnline, setIsBackendOnline] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        // DÝKKAT: PORT 5000!
        const response = await fetch("http://localhost:5000/api/health");
        if (response.ok) {
          setIsBackendOnline(true);
        } else {
          setIsBackendOnline(false);
        }
      } catch (error) {
        console.log("Backend check error:", error);
        setIsBackendOnline(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return { isBackendOnline, isLoading };
};

export default useBackendStatus;
