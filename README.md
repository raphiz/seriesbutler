# Pyseries 0.2.0-dev

Download your favorite TV shows just by running one simple command.

```bash
pyseries path/to/videos/
```

## Usage
Before using pyseries you should create a new directory in which the series are managed.

```bash
mkdir series/
```

Next, you can add new Series using the `add` command. Note that the add keyword is followed by the target directory. If this directory is not provided, the current working directory is used instead.

```bash
pyseries add series/
```

After adding the new series successfully, you can check for new episodes to download. This might take some time - the output will help you understand what's going on. Again: The add keyword is followed by the target directory. If this directory is not provided, the current working directory is used instead.

```bash
pyseries fetch seriess/
```

Here is a quick demo showing the basic usage of pyseries
[![asciicast](https://asciinema.org/a/7q4uku4ws26r4m2dz1m26fhrg.png)](https://asciinema.org/a/7q4uku4ws26r4m2dz1m26fhrg)


## Supported Sites
Pyseries fetches links from the following sites:

* [solarmovie.is](http://solarmovie.is)
* [watchseries.ag](http://watchseries.ag)

The video files are downloaded using [youtube-dl](https://rg3.github.io/youtube-dl/).


## What's next

* Don't look up imdb name on every check - store it in the info file
* Support for more sites
* Some refactorings since the last changes
* Improve performance with the help of generators...
* Prefere links that have a good quality declared (eg. HD or 10/10 video)
* Rethink design -> Eventually use map/filter/sort methods for handling links
