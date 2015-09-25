# Seriesbutler 1.1.0
[![Build Status](https://travis-ci.org/raphiz/seriesbutler.svg)](https://travis-ci.org/raphiz/seriesbutler)
[![Coverage Status](https://coveralls.io/repos/raphiz/seriesbutler/badge.svg?branch=master&service=github)](https://coveralls.io/github/raphiz/seriesbutler?branch=master)
[![Dependency Status](https://www.versioneye.com/user/projects/55f17d5ad4d2040019000060/badge.svg?style=flat)](https://www.versioneye.com/user/projects/55f17d5ad4d2040019000060)

Download your favorite TV shows just by running one simple command.

```bash
seriesbutler fetch
```

## Legal notice
Downloading TV Series may not be legal in your country of residence - please check with your local laws before installing!
The author of this software does not take ANY responsibility for what you do with it!

## Installation
Seriesbutler can be installed using pip. Note that Seriesbutler only supports Python 3.4!

```
sudo pip3 install seriesbutler
```


## Usage
Before using Seriesbutler you should create a new directory in which the series are managed.

```bash
mkdir series/
cd series/
```

We have to initialize the directory to make it work with Seriesbutler.

```bash
seriesbutler init
```

Next, you can add new Series using the `add` command - this should be pretty straight-forward.

```bash
seriesbutler add
```

After adding the new series successfully, you can check for new episodes to download. This might take some time - the command line output will help you understand what's going on.

```bash
seriesbutler fetch
```

Here is a quick demo showing the basic usage of Seriesbutler
[![asciicast](https://asciinema.org/a/e6661ede9noc0fjdjxi5qotxk.png)](https://asciinema.org/a/e6661ede9noc0fjdjxi5qotxk)

For more information, checkout the usage information by calling

```
seriesbutler --help
```

## Supported Sites
Seriesbutler fetches links from the following sites:

* [solarmovie.is](http://solarmovie.is)
* [watchseries.ag](http://watchseries.ag)

The video files are downloaded using [youtube-dl](https://rg3.github.io/youtube-dl/).


## What's next
* There are some TODOs in the code to be resolved
* Support more sites
* Prefere links that have a good quality declared (eg. HD or 10/10 video)
* Improve performance
