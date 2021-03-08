export const environment = {
    production: false,
    apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
    auth0: {
        url: 'happy2000.us', // the auth0 domain prefix
        audience: 'http://localhost/:5000', // the audience set for the auth0 app
        clientId: 'k7ZEqOyBoPUs2zqw5xBHh1ytMrzpma67', // the client id generated for the auth0 app
        callbackURL: 'http://localhost:4200', // the base url of the running ionic application.
    }
};
