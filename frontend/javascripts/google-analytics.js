var cookieObject = Object.fromEntries( document.cookie.split('; ').map( x => x.split('=')) );
// If the analytics cookie is set to true apply GA script tags to end of <head>
if (cookieObject.analytics === 'true') {
  const gaID = document.getElementsByTagName('meta')['site-ga-id'].value;

  let gtm = document.createElement('script');
  gtm.type = 'text/javascript';
  gtm.async = true;
  gtm.src = `https://www.googletagmanager.com/gtag/js?id=${gaID}`;
  document.head.appendChild(gtm);

  let gtag = document.createElement('script');
  gtag.type = 'text/javascript';
  gtag.async = true;
  const inlineScript = document.createTextNode(
    `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)};gtag('js',new Date());gtag('config',${gaID});`
  );
  gtag.appendChild(inlineScript)
};