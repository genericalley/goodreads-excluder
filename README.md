# Goodreads Excluder

I often use Goodreads to find my next book, but my favorite genres have significant crossover with genres that don't interest me.  This script will output an html file containing new releases for desired genres, excluding any book with undesired genres in its top shelves. 

## Getting Started

### Prerequisites

* python3
* pip
* Goodreads developer api key (obtainable [here](https://www.goodreads.com/api/keys))

### Installing

```commandline
python3 -m venv env
source env/bin/activate
pip install -r requirements.pip
```

#### Example

The below command will output a simple html file with covers and links for all new "romance" releases **without** "young-adult" or "novella" in their top 10 shelves
```commandline
python main.py --include=romance --exclude=young-adult,novella --api-key=YOURAPIKEYHERE --threshold=10
```

#### Usage
python main.py [OPTIONS]

| Option      | Type    | Description                                        |
|-------------|---------|----------------------------------------------------|
| --include   | TEXT    | Comma-delimited genres to include                  |
| --exclude   | TEXT    | Comma-delimited genres to exclude                  |
| --api-key   | TEXT    | Goodreads developer api key                        |
| --threshold | INTEGER | Number of top shelves to check for excluded genres |

## Acknowledgments

* Thanks to Goodreads for being an excellent resource and community for readers.
