Title: What's the best subsonic client for Android?
Date: 09-19-2025 16:48
Category: Music

I've been using [Ultrasonic](https://gitlab.com/ultrasonic/ultrasonic) for a
while now, and I have mixed feelings about it. It does the job, for sure, but
it's also been a pain. The UI isn't super intuitive, it's missing the ability to
rate music, and has had [a bug since Dec 2023](https://gitlab.com/ultrasonic/ultrasonic/-/issues?sort=created_date&state=opened&search=rotate&first_page_size=20&show=eyJpaWQiOiIxMjgxIiwiZnVsbF9wYXRoIjoidWx0cmFzb25pYy91bHRyYXNvbmljIiwiaWQiOjE0MDE4ODA4NH0%3D)
which resets playback, and duplicates the now playing queue whenever you rotate
the screen.

I finally got annoyed enough to see what else is out there! So...

# What else is out there?

I looked at all 5 different subsonic API clients that were [available to download
from F-Droid](https://search.f-droid.org/?q=subsonic&lang=en) (Funkwhale doesn't
use the subsonic API, DSub hasn't been updated since 2022)

1. [Ultrasonic](https://gitlab.com/ultrasonic/ultrasonic)
2. [YouAMP](https://github.com/siper/YouAMP)
3. [Tempo](https://github.com/CappielloAntonio/tempo)
4. [subtracks](https://github.com/austinried/subtracks)
5. [DSub2000](https://github.com/paroj/DSub2000)

I've heard [good
things](https://www.reddit.com/r/selfhosted/comments/uvwfh1/any_uptodate_subsonic_client_for_android/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)
about [symfonium](https://www.symfonium.app/) but it's not free nor open source,
so I feel like I have to at least investigate other options before I go down
that road.

# What makes a good subsonic API client?

This obviously varies from person to person, which is probably why there are so
many different clients out there! But I have a pretty long list of features that
I'd like to have, and some are more important than others. So, I wrote down
which features I felt were nice while I interacted with the various apps for a
while and came up with this list, roughly sorted by importance.

1. MPD Style Queuing
2. Scrobbling
3. Playlist Management
4. Lock screen widget functionality
5. Starring
6. Sharing
7. Rating
8. Intuitive Interface
9. Download Songs
10. Mix/Radio/Autoplay Function
11. Seamless Offline Playback

The first thing you might notice is that "playing music" isn't one of the
features. There's a few things that I take for granted when I install a music
client. If you can't play music, skip songs, search, etc. then you aren't even
worth considering. The above features are all supported at varying levels
by the applications in question.

The next thing you might notice is that it isn't obvious what some of those
things mean exactly. That's fair! They're meaning isn't super obvious, but
it'll make more sense to show what's what first then explain them afterward.

# The Big Table O' Features

App        | MPD Style Queuing             | Scrobbling                | Playlist Management | Lock screen widget functionality                          | Starring                               | Sharing                    | Rating           | Intuitive Interface | Download Songs      | Mix/Radio/Autoplay Function     | Seamless Offline Playback
---------- | -----------------             | ----------                | ------------------- | --------------------------------                          | --------                               | -------                    | ------           | ------------------- | --------------      | ---------------------------     | -------------------------
Ultrasonic | Yes { .cell-green }           | Yes { .cell-green }       | No { .cell-red }    | Prev, Scrub, Star, Shuffle, Pause { .cell-lightgreen }    | Albums, Songs { .cell-lightgreen }     | Yes { .cell-green }        | No { .cell-red }           | No { .cell-red }                  | Yes { .cell-green } | No { .cell-red }                | No { .cell-red }
YouAMP     | Songs only { .cell-lightred } | No { .cell-red }          | No { .cell-red }    | None { .cell-red }                                        | Artists, Albums, Songs { .cell-green } | No { .cell-red }           | No { .cell-red }           | Yes { .cell-green }               | No { .cell-red }    | No { .cell-red }                | No { .cell-red }
Tempo      | Yes { .cell-green }           | Yes { .cell-green }       | Yes { .cell-green } | Prev, Next, Scrub, Pause { .cell-lightred }               | Artists, Albums, Songs { .cell-green } | Yes* { .cell-lightgreen }  | Songs { .cell-lightred }           | Yes* { .cell-lightgreen } | Yes { .cell-green } | Yes*  { .cell-lightgreen }      | No { .cell-red }
subtracks  | No  { .cell-red }             | Yes* { .cell-lightgreen } | No { .cell-red }    | Prev, Next, Scrub, Pause, Stop { .cell-lightred }         | Artists, Albums, Songs { .cell-green } | No { .cell-red }           | No { .cell-red }           | Yes  { .cell-green}               | No { .cell-red }    | No { .cell-red }                | No { .cell-red }
DSub2000   | Yes { .cell-green }	       | Yes  { .cell-green }      | Yes { .cell-green } | Prev, Next, Scrub, Dislike, Star, Pause* { .cell-yellow } | Artists, Albums, Songs { .cell-green } | Yes*  { .cell-lightgreen } | Albums { .cell-lightred }  | No { .cell-red }                  | Yes { .cell-green } | No* { .cell-lightred }          | No { .cell-red }

This table tries to capture which apps support what and to what degree.
Unfortunately, some of these items have varying degrees to which they can be
supported, so it's not obvious how to rate them all, but the color approximates
how good of support the app has for the feature.

Now I'll explain what each of these categories mean so that it's clear, and
explain what any asterisks mean in the table.

### MPD Style Queuing

[MPD](https://www.musicpd.org/) is an old music player. The way that you play
music in it is by adding songs to ["the
queue"](https://mpd.readthedocs.io/en/stable/user.html#the-queue). So to play a
playlist you just copy over the songs from the playlist to the queue. To play an
album you copy it over to the queue. If you want to play two albums in sequence
you add first to the queue, then add the second to the back of the queue. It's
very intuitive and very powerful. This is also how many steaming services and
music apps work nowadays, but I have seen ones that don't work like this. I'm
pretty sure iTunes used to only let you play playlists that you build, albums,
or individual songs. That _does not_ work with the way I listen to music. This
is my most important feature for sure.

**YouAMP**: Only allows you to queue songs, not albums and subtracks doesn't
allow queuing of any kind other than playing an album as far as I could tell.

**DSub2000**: It's probably worth noting that you have to enable an option to
allow you to queue an album - Enabled `Settings > Appearance > Play Last`.

### Scrobbling

Scrobbling is a term for tracking how many times you've played a song. I
scrobble to [listenbrainz](https://listenbrainz.org/user/ToxicGLaDOS/), but
other people might scrobble to [last.fm](https://last.fm). Keeping track of
what I listen to is somehow about as important to me as listening itself. It's
a bit obsessive.

**YouAMP**: I wasn't able to find a way to enable scrobbling

**DSub2000**: I couldn't find a way to disable it. Every other app allows you to
disable it, but I personally don't care about that.
subtracks: It works, but it scrobbles as soon as you start the song, so you
don't get a "now listening" on listenbrainz, which is lame.

### Playlist Management

This is pretty self explanatory, albeit a little surprising that it isn't
totally standard behavior. I want to be able to create and delete playlists, as
well as add, remove, and reorder songs in a playlist.

### Lock screen widget functionality

Here's the images of the lock screen widgets. They mostly look the same other
than what buttons they expose, except for YouAMP which doesn't have one.

#### Ultrasonic
![Ultrasonic's lock screen widget](lock_screen_widget_ultrasonic.jpg "Ultrasonic's lock screen widget"){: width=500 }

#### Tempo
![Tempo's lock screen widget](lock_screen_widget_tempo.jpg "Tempo's lock screen widget"){: width=500 }

#### subtracks
![subtracks's lock screen widget](lock_screen_widget_subtracks.jpg "subtracks's lock screen widget"){: width=500 }

#### DSub2000
![DSub2000's lock screen widget](lock_screen_widget_dsub2000.jpg "DSub2000's lock screen widget"){: width=500 }

The lock screen widget is very important to me. I get most of my music listening
done in the car. I don't want to have to mess around with unlocking my phone or
navigating through the app to do some basic things such as skip, or star a song.
The color is based on those two buttons that I care about - star and next.

**DSub2000**: This one seems like it should be the best by a lot, but there's
currently an issue where pausing closes the widget so you can't start playing
the song again without opening up the app again. Essentially, it functions as a
stop button which makes it unuseable in my opinion. DSub2000 has approximately a
million config options, (which is awesome!), but I couldn't find one that fixes
this behavior. I can't say it doesn't exist though, so yellow for you!

### Starring

Different apps call it different things. Favorite, Like, Star, etc. Subsonic
refers to it as [star](https://subsonic.org/pages/api.jsp#star) so that's what
I'll call it. Starring is just one of the few ways that you can categorize your
music and I want to be able to use it!

Ultrasonic: You can't star artists, not a big deal, but everyone else managed to
do it right.

### Sharing

If your server supports it you can share your music with other people even if
they don't have an account by sharing a special link with them. Some apps have a
way to get these links from the server natively. This is pretty nice to have so
that I don't have to log into Navidrome's web UI to share music.

**YouAMP**: Doesn't support sharing

**Tempo**: No config options when sharing

**subtracks**: Doesn't support sharing

**DSub2000**: No config options when sharing

### Rating

[Rating](https://subsonic.org/pages/api.jsp#setRating) is similar but distinct
from starring. Starring has two states, starred or unstarred. Rating has 6
states, 1-5 stars or 0 stars which represents unrated. I listen to a lot of
music that doesn't make it easy to remember the titles of songs. Having a way to
rank music gives me a way to easily choose between my favorites, mostly good
stuff, or stuff I haven't yet rated depending on how I'm feeling.

**Tempo**: Only supports rating individual songs

**DSub2000**: Only supports rating whole albums

It is possible to rate artists in subsonic, but none of these apps support it.

### Intuitive Interface

The meaning is obvious, but what makes an Intuitive Interface depends on the
person and which features they're trying to use. This is just a subjective
measure of how many times I had trouble finding something, or accidentally took
an action I didn't mean to. Every interface has it's quirks, but some are truly
strange.

**Ultrasonic**: The symbols don't have obvious meanings until you click around the
first time to memorize them. When you're on an album there's a play button up in
the top right which plays the whole album which isn't the place that I expect
the play button to be (bottom-center). It gets even more confusing when you have
a song selected in the same menu. In this case, there's two play buttons that
each do different things, top right plays the album, bottom left plays the
selected songs. I think it's not a great design that you can end up in this
confusing situation.

**Tempo**: Tempo's interface is mostly intuitive, but the media library page is very
strange. There's basically not options in it other than to look around by folder
and play individual songs. There's albums listed, and yet you can only play
songs... Weird. If you ignore that page it's pretty understandable.

**DSub2000**: My main complaint here is with the "Now Playing" page. I think the
below gif (with director commentary) will illustrate why.

I start by opening what I would call the "now playing" screen by clicking on the
bottom bar, fair enough... But then it gets weird already. I tap on the album
art, I'm not exactly sure what I think this should do (probably nothing?), but
it takes me to the queue.. Interesting. The list-with-music-note button is still
on the bottom right though, that usually is the button to show you the queue.
What happens if I click that? Brings you back to the album art. K... I guess
that's not thaaaat weird, but I don't love that the symbol for go to the queue
and return from the queue is the same. Then I tap the back arrow on the top left
and that brings me back to where I was, good stuff.

Okay, so that's not too bad, but it get's more confusing. I open the "now
playing" screen again to the album art, tap the album art to see the queue and
now I want to go back to the album art. So what do I do? I click the back arrow!
But as previously discussed, that takes you back to the previous screen. Not the
previous screen _in this context_, nonono, it's the previous screen where we
were selecting songs from the album (where the video started), but they look
almost identical and have _almost_ identical long press and triple dot menu
options, but not _actually_ identical!

Not ideal so far, but what else could there be on one screen? Let's open up the
"now playing" screen one more time. The three dots in top left might have
something interesting **tap**. Hmmmm "Remove all"... Sounds like it'll remove all
the songs from the queue. Too bad I can't see any of them from this screen.
"Exit", what does that do? Use your buzzer to guess now

1. Just close the menu
2. Close the "now playing screen" and return to the album view
3. Close the whole app
4. Stop playing the current song

Watch the gif to find out.

![DSub2000 now playing screen interaction](dsub_now_playing.gif "DSub2000 now playing screen interaction"){: height=500 }

Ah of course, it closes the whole app. That probably makes the most sense of
those options, but why is that even a menu option? The worst part is that "Exit"
is only there on the triple dot menu on the "now playing" screen! This is the
album view with the triple dot menu open:

![DSub2000 album view context menu](dsub_album_view_context_menu.jpg "DSub2000 album view context menu"){: height=500 }

I don't know what to say...

### Download Songs

This is the ability to download songs while online and play them back later when
you're not connected to the internet. I think that most people desire this
feature more than I do, because it's listed as one of the highlighted features
in every app that supports it. I think I've used it one time in the last 3
years. It's nice to have in a pinch though.

### Mix/Radio/Autoplay function

This is the ability to generate a queue on the fly of similar songs. There's a
few different implementations that are more or less the same for me. You can add
songs to the queue after all the manually queued ones, you can offer a "radio"
or "mix" button which will play similar songs, anything like that would work for
me really. I don't really need this, but sometimes when I'm in the car I don't
want to queue up more stuff and would rather just let the app decide.

**Tempo**: I didn't try this extensively, but it seems to only play songs by the
same artist, which is nice I guess? But I could just shuffle a few albums around
and get similar results, I want a little more than that. It technically does
have the feature though, so light green for you.

**DSub2000**: I thought they didn't have an option at first, but when I dug around a
little I noticed a radio icon when you're looking at an artist. Cool! "They
can't generate it from albums, but at least they have something" I thought to
myself. Then I clicked it and it brings me to the "Now Playing" screen with
nothing in the queue. Everytime. I don't know if this is a feature in progress
or what, but it doesn't work, so it doesn't count.

### Seamless Offline Playback

My desire for this comes from my experience with offline playback in Ultrasonic.
To do offline playback in Ultrasonic you need to switch servers to the "offline"
server. This was very unintuitive to me and also meant that you can't switch
back the online mode without more manual intervention. The idea here is to only
show the songs that are available to you at any given time. If you lose
connectivity then the available songs are just the ones that you have downloaded
currently, and when you come back online you see the full library again.
Unfortunately for me, this was just a dream feature, because no app I tested
supported it. :(

# Conclusions!

I think that someone could choose Tempo or DSub2000 and have that be a good
choice for them, but I think [Tempo](https://github.com/CappielloAntonio/tempo)
is going to be the one for me. I'll probably also try out
[DSub2000](https://github.com/paroj/DSub2000) for a little while too just to
make sure I'm not missing out.

It's pretty close overall, but I like the UI a lot more on Tempo and DSub2000
has that one killer bug(?) with the lock screen widget. The features that I'm
missing from Tempo seem like they could be easy enough to implement myself, (in
theory without actually looking at their code yet haha), so if I just need to
add a few buttons I can ~~do~~ try that, and I certainly can't overhaul the UI of
DSub2000, so even if Tempo was a little worse I'd have more options with Tempo
anyways.

It's worth noting that Tempo hasn't been actively maintained in 8 months or so,
but some forks have popped up to try to keep prs flowing. I tried
[eddyizm/tempo](https://github.com/eddyizm/tempo) for just a little while and
noticed that they added some more buttons to the lock screen widget, but no star
option yet. At least changes are coming in here to this one.

Unless something changes I don't think the other three are going to do it for
_me_. If you're looking for a different set of features, then you might like a
different application more. For instance, YouAMP is very simple and hard mess
things up. It just doesn't work out with the way I like to listen to music.
Subtracks can't queue songs the way I want either, so that one's out. All
that's left is Ultrasonic which I've been using for a couple years, but that
why I'm here - I'm not satisfied with it.

If you know about any clients I haven't tested, or if I've made a mistake in my
evaluation of these features let me know by email at
[jeff@blackolivepineapple.pizza](mailto:jeff@blackolivepineapple.pizza) :)
