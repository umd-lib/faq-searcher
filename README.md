# faq-searcher

Python 3 Flask application to search the libanswers FAQ searcher.

## Requires

* Python 3.10.8

### Development Setup

See [docs/DevelopmentSetup.md](docs/DevelopmentSetup.md).

## Environment Configuration

The application requires a ".env" file in the root directory to provide
server-specific information (i.e., those parts of the configuration that
may vary based on whether the server is a test/qa/production server).

A sample "env_example" file has been provided to assist with this process.
Simply copy the "env_example" file to ".env" and fill out the parameters as
appropriate.

The configured .env file should not be checked into the Git repository.

### Running in Docker

```bash
$ docker build -t docker.lib.umd.edu/faq-searcher .
$ docker run -it --rm -p 5000:5000 --env-file=.env --read-only docker.lib.umd.edu/faq-searcher
```

### Building for Kubernetes

```bash
$ docker buildx build . --builder=kube -t docker.lib.umd.edu/faq-searcher:VERSION --push
```

### Endpoints

This will start the webapp listening on the default port 5000 on localhost
(127.0.0.1), and running in [Flask's debug mode].

Root endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/>

/ping endpoint (just returns `{status: ok}` to all requests):
<http://localhost:5000/ping>

/search:

```bash
http://localhost:5000/search?q=print&per_page=3&page=0
```

Example:

```bash
curl 'http://localhost:5000/search?q=print&per_page=3&page=0'
{
  "endpoint": "faq",
  "module_link": "http://umd.libanswers.com/search?q=print",
  "page": 0,
  "per_page": 3,
  "query": "print",
  "results": [
    {
      "description": "Photocopying, Printing, Library 101",
      "item_format": "web_page",
      "link": "https://umd.libanswers.com/faq/66289",
      "title": "How do I print?"
    },
    {
      "description": "Printing, Makerspace",
      "item_format": "web_page",
      "link": "https://umd.libanswers.com/faq/66460",
      "title": "Can I 3D Print in two different colors?"
    },
    {
      "description": "Photocopying, Printing, Library 101",
      "item_format": "web_page",
      "link": "https://umd.libanswers.com/faq/66032",
      "title": "How can I print and/or make copies?"
    }
  ],
  "total": 42
}
```

[Flask's debug mode]: https://flask.palletsprojects.com/en/2.2.x/cli/?highlight=debug%20mode

## License

See the [LICENSE](LICENSE.txt) file for license rights and limitations.
