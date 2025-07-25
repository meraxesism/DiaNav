// @ts-nocheck
// Fix for web-vitals v3+ API

const reportWebVitals = (onPerfEntry?: any) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then((webVitals) => {
      webVitals.getCLS && webVitals.getCLS(onPerfEntry);
      webVitals.getFID && webVitals.getFID(onPerfEntry);
      webVitals.getFCP && webVitals.getFCP(onPerfEntry);
      webVitals.getLCP && webVitals.getLCP(onPerfEntry);
      webVitals.getTTFB && webVitals.getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals;
