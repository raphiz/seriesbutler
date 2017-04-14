# DISCONTINUED!
# Seriesbutler 1.3.0-dev
[![Build Status](https://travis-ci.org/raphiz/seriesbutler.svg)](https://travis-ci.org/raphiz/seriesbutler)
[![codecov.io](https://codecov.io/github/raphiz/seriesbutler/coverage.svg?branch=master)](https://codecov.io/github/raphiz/seriesbutler?branch=master)
[![Dependency Status](https://www.versioneye.com/user/projects/55f17d5ad4d2040019000060/badge.svg?style=flat)](https://www.versioneye.com/user/projects/55f17d5ad4d2040019000060)

Download your favourite TV shows just by running one simple command.

```bash
seriesbutler fetch
```

## Legal notice
Downloading TV Series may not be legal in your country of residence - please check with your local laws before installing!
The author of this software does not take ANY responsibility for what you do with it!

## Installation
Seriesbutler can be installed using pip. Note that Seriesbutler only supports Python >= 3.4!

```
sudo pip3 install seriesbutler
```


## Usage
Why should you use Seriesbutler? There are two major reasons: You want your home server to
grab the series for you - so that they are ready for you to watch when you want to or you just
want to use the command line - instead of clicking all the ads away.

Before using Seriesbutler, you should create a new directory in which the series are managed.

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

### Configuration
You can manually modify the Seriesbutler configuration - it's a simple plain JSON file called
`Seriesbutler.json` located in the Seriesbutler working directory.

The full [JSON Schema](http://json-schema.org/) can be found [here](https://github.com/raphiz/seriesbutler/blob/master/seriesbutler/models.py#L27)

#### hosters (required)
Some hosters might have a terrible video quality while others are fast and good. This
option allows you to specify preferred hosters, which will instruct Seriesbutler to look for
give preference to the links of this hoster.

The ignored list specifies hosters which will be completely ignored, even if no other links
are available.

Note that these rules match if a host name *starts with* one of the specified hoster names -
if you specify *played* for example, it will apply for *http://played.to/* as well as *http://played-stuff.xyz/*.

The order in which the preferred links are checked is the same as declared here.

```json
{
    "hosters": {
        "ignored": [
            "played",
            "vodlocker"
        ],
        "preferred": [
            "vidspot.net",
            "allmyvideos.net"            
        ]
    }
}
```

#### series (required)
The series array contains zero or more TV series elements which Seriesbutler will keep
track of. Use the command line option `seriesbutler add` and `seriesbutler remove`
instead of manually edit this option - it's much simpler!

```json
{
    "series": [
        {
            "imdb": "tt1586680",
            "name": "Shameless (US)",
            "start_from": {
                "season": 5,
                "episode": 9
            }
        }
    ]
}
```

#### ydl_options (optional)
This is the most flexible - but most complicated option. It allows you to directly pass
options to [youtube-dl](https://rg3.github.io/youtube-dl/) - as if you were using its API
directly. This is very useful if you prefer a certain format or want to use an alternative downloader etc.

Checkout the [youtube-dl README](https://github.com/rg3/youtube-dl/blob/master/README.md) for all supported options.

```json
{
    "ydl_options" : {
        "recodevideo" : "mp4",
        "external_downloader": "axel",
        "external_downloader_args": ["-a"]
    }
}
```

## Supported Sites
Seriesbutler fetches links from the following sites:

* [putlocker-series.com](http://putlocker-series.com) - since version v1.3.0
* [solarmovie.ph](http://solarmovie.ph)
* [watchseries.ag](http://watchseries.ag)

The video files are downloaded using [youtube-dl](https://rg3.github.io/youtube-dl/).


## What's next
* There are some TODOs in the code to be resolved
* Support more sites
* Prefer links that have a good quality declared (eg. HD or 10/10 video)
* Improve performance
