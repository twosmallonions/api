import express, { NextFunction, Request, Response } from 'express';
import { expressjwt as jwt, UnauthorizedError } from 'express-jwt';
import { expressJwtSecret } from 'jwks-rsa';

const app = express()

app.use(jwt({
    secret: expressJwtSecret({
        cache: true,
        rateLimit: true,
        jwksRequestsPerMinute: 1,
        jwksUri: 'https://auth-ng.meschter.me/realms/tso_dev/protocol/openid-connect/certs'
    }),
    audience: 'tso-api',
    issuer: 'https://auth-ng.meschter.me/realms/tso_dev',
    algorithms: ['RS256', 'ES256'],
    
}))

app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
    if (err instanceof UnauthorizedError) {
        console.error(`jwt verification failed: ${err.code}`);
        res.setHeader('WWW-Authenticate', `Bearer error=${err.code} error_description=${err.message}`)
        res.status(401).send();
        return;
    }
    console.error(err.stack);
    res.status(500).send('something broke!');
})

const port = 3000;

app.get('/', (req, res) => {
    res.send('Hello World!');
});

app.listen(port, () => {
    console.log(`api listening on port ${port}`)
})